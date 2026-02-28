"""Recording model for video recordings"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.camera import Camera
    from app.models.video_metadata import VideoMetadata
    from app.models.event import Event


class Recording(Base):
    """Recording model for storing video recording information"""
    
    __tablename__ = "recordings"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    camera_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    recording_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="motion",
        server_default="motion",
        index=True
    )
    start_time: Mapped[str] = mapped_column(Text, nullable=False, index=True)
    end_time: Mapped[str] = mapped_column(Text, nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    duration: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_encrypted: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    encryption_key: Mapped[str | None] = mapped_column(String(255), nullable=True)
    codec: Mapped[str | None] = mapped_column(String(20), nullable=True)
    resolution_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resolution_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    bitrate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat()
    )
    
    # Relationships
    camera: Mapped["Camera"] = relationship(
        "Camera",
        back_populates="recordings"
    )
    video_metadata: Mapped["VideoMetadata"] = relationship(
        "VideoMetadata",
        back_populates="recording",
        uselist=False,
        cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="recording"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "recording_type IN ('continuous', 'motion', 'scheduled')",
            name="check_recordings_recording_type"
        ),
        CheckConstraint("is_encrypted IN (0, 1)", name="check_recordings_is_encrypted"),
    )
    
    def __repr__(self) -> str:
        return f"<Recording(id={self.id}, camera_id={self.camera_id}, type='{self.recording_type}')>"
    
    def is_motion_recording(self) -> bool:
        """Check if this is a motion-triggered recording"""
        return self.recording_type == "motion"
    
    def is_continuous_recording(self) -> bool:
        """Check if this is a continuous recording"""
        return self.recording_type == "continuous"
    
    def is_scheduled_recording(self) -> bool:
        """Check if this is a scheduled recording"""
        return self.recording_type == "scheduled"
    
    def is_encrypted_recording(self) -> bool:
        """Check if recording is encrypted"""
        return self.is_encrypted == 1
    
    def get_file_size_mb(self) -> float:
        """Get file size in megabytes"""
        return self.file_size / (1024 * 1024)
    
    def get_file_size_gb(self) -> float:
        """Get file size in gigabytes"""
        return self.file_size / (1024 * 1024 * 1024)
    
    def get_duration_minutes(self) -> float:
        """Get duration in minutes"""
        return self.duration / 60
    
    def get_resolution(self) -> tuple[int, int] | None:
        """Get resolution as tuple"""
        if self.resolution_width and self.resolution_height:
            return (self.resolution_width, self.resolution_height)
        return None
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert recording to dictionary"""
        data = {
            "id": self.id,
            "camera_id": self.camera_id,
            "file_path": self.file_path,
            "recording_type": self.recording_type,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "file_size": self.file_size,
            "file_size_mb": round(self.get_file_size_mb(), 2),
            "duration": self.duration,
            "duration_minutes": round(self.get_duration_minutes(), 2),
            "is_encrypted": self.is_encrypted == 1,
            "encryption_key": self.encryption_key if include_sensitive else None,
            "codec": self.codec,
            "resolution_width": self.resolution_width,
            "resolution_height": self.resolution_height,
            "bitrate": self.bitrate,
            "created_at": self.created_at,
        }
        return data
