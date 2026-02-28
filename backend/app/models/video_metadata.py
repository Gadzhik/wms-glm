"""Video metadata model for recording metadata"""
from typing import TYPE_CHECKING

from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.recording import Recording


class VideoMetadata(Base):
    """Video metadata model for storing recording metadata"""
    
    __tablename__ = "video_metadata"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recording_id: Mapped[int] = mapped_column(
        ForeignKey("recordings.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    thumbnails: Mapped[str | None] = mapped_column(Text, nullable=True)
    detected_objects: Mapped[str | None] = mapped_column(Text, nullable=True)
    motion_events: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Relationships
    recording: Mapped["Recording"] = relationship(
        "Recording",
        back_populates="video_metadata"
    )
    
    def __repr__(self) -> str:
        return f"<VideoMetadata(id={self.id}, recording_id={self.recording_id})>"
    
    def get_thumbnails(self) -> list:
        """Parse and return thumbnails list"""
        import json
        if self.thumbnails:
            try:
                return json.loads(self.thumbnails)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def get_detected_objects(self) -> list:
        """Parse and return detected objects list"""
        import json
        if self.detected_objects:
            try:
                return json.loads(self.detected_objects)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def get_motion_events(self) -> list:
        """Parse and return motion events list"""
        import json
        if self.motion_events:
            try:
                return json.loads(self.motion_events)
            except (json.JSONDecodeError, TypeError):
                return []
        return []
    
    def set_thumbnails(self, thumbnails: list) -> None:
        """Set thumbnails from list"""
        import json
        self.thumbnails = json.dumps(thumbnails)
    
    def set_detected_objects(self, objects: list) -> None:
        """Set detected objects from list"""
        import json
        self.detected_objects = json.dumps(objects)
    
    def set_motion_events(self, events: list) -> None:
        """Set motion events from list"""
        import json
        self.motion_events = json.dumps(events)
    
    def add_detected_object(self, obj: dict) -> None:
        """Add a detected object"""
        objects = self.get_detected_objects()
        objects.append(obj)
        self.set_detected_objects(objects)
    
    def add_motion_event(self, event: dict) -> None:
        """Add a motion event"""
        events = self.get_motion_events()
        events.append(event)
        self.set_motion_events(events)
    
    def get_person_count(self) -> int:
        """Get count of detected persons"""
        objects = self.get_detected_objects()
        return sum(1 for obj in objects if obj.get("type") == "person")
    
    def to_dict(self) -> dict:
        """Convert video metadata to dictionary"""
        return {
            "id": self.id,
            "recording_id": self.recording_id,
            "thumbnails": self.get_thumbnails(),
            "detected_objects": self.get_detected_objects(),
            "motion_events": self.get_motion_events(),
            "person_count": self.get_person_count(),
        }
