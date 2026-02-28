"""Camera model for IP cameras"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Text, Float, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.recording import Recording
    from app.models.event import Event
    from app.models.schedule import Schedule


class Camera(Base):
    """Camera model for storing IP camera information"""
    
    __tablename__ = "cameras"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    rtsp_url: Mapped[str] = mapped_column(String(500), nullable=False)
    onvif_host: Mapped[str | None] = mapped_column(String(100), nullable=True)
    onvif_port: Mapped[int | None] = mapped_column(Integer, nullable=True, default=80)
    onvif_username: Mapped[str | None] = mapped_column(String(50), nullable=True)
    onvif_password: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="offline",
        server_default="offline",
        index=True
    )
    recording_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="motion",
        server_default="motion"
    )
    detection_enabled: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1"
    )
    detection_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.5,
        server_default="0.5"
    )
    resolution_width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resolution_height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    codec: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fps: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat()
    )
    updated_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat()
    )
    
    # Relationships
    recordings: Mapped[list["Recording"]] = relationship(
        "Recording",
        back_populates="camera",
        cascade="all, delete-orphan"
    )
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="camera"
    )
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule",
        back_populates="camera",
        cascade="all, delete-orphan"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint("status IN ('online', 'offline', 'error')", name="check_cameras_status"),
        CheckConstraint(
            "recording_mode IN ('continuous', 'motion', 'scheduled')",
            name="check_cameras_recording_mode"
        ),
        CheckConstraint(
            "detection_confidence >= 0 AND detection_confidence <= 1",
            name="check_cameras_detection_confidence"
        ),
        CheckConstraint("detection_enabled IN (0, 1)", name="check_cameras_detection_enabled"),
    )
    
    def __repr__(self) -> str:
        return f"<Camera(id={self.id}, name='{self.name}', status='{self.status}')>"
    
    def is_online(self) -> bool:
        """Check if camera is online"""
        return self.status == "online"
    
    def is_offline(self) -> bool:
        """Check if camera is offline"""
        return self.status == "offline"
    
    def has_error(self) -> bool:
        """Check if camera has error"""
        return self.status == "error"
    
    def is_detection_enabled(self) -> bool:
        """Check if detection is enabled"""
        return self.detection_enabled == 1
    
    def get_resolution(self) -> tuple[int, int] | None:
        """Get camera resolution as tuple"""
        if self.resolution_width and self.resolution_height:
            return (self.resolution_width, self.resolution_height)
        return None
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """Convert camera to dictionary"""
        data = {
            "id": self.id,
            "name": self.name,
            "rtsp_url": self.rtsp_url if include_sensitive else "***",
            "onvif_host": self.onvif_host,
            "onvif_port": self.onvif_port,
            "onvif_username": self.onvif_username if include_sensitive else None,
            "onvif_password": self.onvif_password if include_sensitive else None,
            "status": self.status,
            "recording_mode": self.recording_mode,
            "detection_enabled": self.detection_enabled == 1,
            "detection_confidence": self.detection_confidence,
            "resolution_width": self.resolution_width,
            "resolution_height": self.resolution_height,
            "codec": self.codec,
            "fps": self.fps,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
        return data
    
    @property
    def onvif_url(self) -> str | None:
        """Get ONVIF URL if configured"""
        if self.onvif_host and self.onvif_port:
            return f"http://{self.onvif_host}:{self.onvif_port}/onvif/device_service"
        return None
