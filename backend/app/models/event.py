"""Event model for system events"""
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import String, Integer, Text, ForeignKey, CheckConstraint, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.database import Base

if TYPE_CHECKING:
    from app.models.camera import Camera
    from app.models.recording import Recording


class Event(Base):
    """Event model for storing system events"""
    
    __tablename__ = "events"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    camera_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    recording_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("recordings.id", ondelete="SET NULL"),
        nullable=True
    )
    timestamp: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat(),
        index=True
    )
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # LLM-generated description
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Semantic search embedding (pgvector)
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(768),
        nullable=True
    )
    
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="new",
        server_default="new",
        index=True
    )
    push_sent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0"
    )
    
    # Relationships
    camera: Mapped["Camera"] = relationship(
        "Camera",
        back_populates="events"
    )
    recording: Mapped["Recording"] = relationship(
        "Recording",
        back_populates="events"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "event_type IN ('motion_detected', 'person_detected', 'camera_offline', "
            "'camera_error', 'storage_full', 'system_error')",
            name="check_events_event_type"
        ),
        CheckConstraint(
            "status IN ('new', 'acknowledged', 'resolved')",
            name="check_events_status"
        ),
        CheckConstraint("push_sent IN (0, 1)", name="check_events_push_sent"),
    )
    
    # Event type constants
    EVENT_TYPE_MOTION_DETECTED = "motion_detected"
    EVENT_TYPE_PERSON_DETECTED = "person_detected"
    EVENT_TYPE_CAMERA_OFFLINE = "camera_offline"
    EVENT_TYPE_CAMERA_ERROR = "camera_error"
    EVENT_TYPE_STORAGE_FULL = "storage_full"
    EVENT_TYPE_SYSTEM_ERROR = "system_error"
    
    # Status constants
    STATUS_NEW = "new"
    STATUS_ACKNOWLEDGED = "acknowledged"
    STATUS_RESOLVED = "resolved"
    
    def __repr__(self) -> str:
        return f"<Event(id={self.id}, type='{self.event_type}', status='{self.status}')>"
    
    def is_motion_event(self) -> bool:
        """Check if this is a motion detection event"""
        return self.event_type == self.EVENT_TYPE_MOTION_DETECTED
    
    def is_person_event(self) -> bool:
        """Check if this is a person detection event"""
        return self.event_type == self.EVENT_TYPE_PERSON_DETECTED
    
    def is_camera_event(self) -> bool:
        """Check if this is a camera-related event"""
        return self.event_type in (self.EVENT_TYPE_CAMERA_OFFLINE, self.EVENT_TYPE_CAMERA_ERROR)
    
    def is_system_event(self) -> bool:
        """Check if this is a system event"""
        return self.event_type in (self.EVENT_TYPE_STORAGE_FULL, self.EVENT_TYPE_SYSTEM_ERROR)
    
    def is_new(self) -> bool:
        """Check if event status is new"""
        return self.status == self.STATUS_NEW
    
    def is_acknowledged(self) -> bool:
        """Check if event status is acknowledged"""
        return self.status == self.STATUS_ACKNOWLEDGED
    
    def is_resolved(self) -> bool:
        """Check if event status is resolved"""
        return self.status == self.STATUS_RESOLVED
    
    def is_push_sent(self) -> bool:
        """Check if push notification was sent"""
        return self.push_sent == 1
    
    def get_details(self) -> dict:
        """Parse and return event details"""
        import json
        if self.details:
            try:
                return json.loads(self.details)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_details(self, details: dict) -> None:
        """Set event details from dictionary"""
        import json
        self.details = json.dumps(details)
    
    def acknowledge(self) -> None:
        """Mark event as acknowledged"""
        self.status = self.STATUS_ACKNOWLEDGED
    
    def resolve(self) -> None:
        """Mark event as resolved"""
        self.status = self.STATUS_RESOLVED
    
    def mark_push_sent(self) -> None:
        """Mark push notification as sent"""
        self.push_sent = 1
    
    def to_dict(self) -> dict:
        """Convert event to dictionary"""
        return {
            "id": self.id,
            "event_type": self.event_type,
            "camera_id": self.camera_id,
            "recording_id": self.recording_id,
            "timestamp": self.timestamp,
            "details": self.get_details(),
            "status": self.status,
            "push_sent": self.push_sent == 1,
            "description": self.description,
            "has_embedding": self.embedding is not None,
        }
