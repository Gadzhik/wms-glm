"""Schedule model for recording schedules"""
from typing import TYPE_CHECKING

from sqlalchemy import String, Integer, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.camera import Camera


class Schedule(Base):
    """Schedule model for storing recording schedules"""
    
    __tablename__ = "schedules"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    camera_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cameras.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    days_of_week: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[str] = mapped_column(String(5), nullable=False)
    end_time: Mapped[str] = mapped_column(String(5), nullable=False)
    record_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="continuous",
        server_default="continuous"
    )
    is_active: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default="1",
        index=True
    )
    
    # Relationships
    camera: Mapped["Camera"] = relationship(
        "Camera",
        back_populates="schedules"
    )
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "record_type IN ('continuous', 'motion')",
            name="check_schedules_record_type"
        ),
        CheckConstraint("is_active IN (0, 1)", name="check_schedules_is_active"),
    )
    
    # Day of week constants
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    
    # Record type constants
    RECORD_TYPE_CONTINUOUS = "continuous"
    RECORD_TYPE_MOTION = "motion"
    
    def __repr__(self) -> str:
        return f"<Schedule(id={self.id}, camera_id={self.camera_id}, active={self.is_active})>"
    
    def is_active_schedule(self) -> bool:
        """Check if schedule is active"""
        return self.is_active == 1
    
    def is_continuous_record(self) -> bool:
        """Check if schedule uses continuous recording"""
        return self.record_type == self.RECORD_TYPE_CONTINUOUS
    
    def is_motion_record(self) -> bool:
        """Check if schedule uses motion recording"""
        return self.record_type == self.RECORD_TYPE_MOTION
    
    def get_days_of_week(self) -> list[int]:
        """Parse and return days of week list"""
        import json
        try:
            return json.loads(self.days_of_week)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def set_days_of_week(self, days: list[int]) -> None:
        """Set days of week from list"""
        import json
        self.days_of_week = json.dumps(days)
    
    def is_day_scheduled(self, day: int) -> bool:
        """Check if specific day is scheduled"""
        return day in self.get_days_of_week()
    
    def is_weekend_scheduled(self) -> bool:
        """Check if weekend is scheduled"""
        days = self.get_days_of_week()
        return self.SATURDAY in days or self.SUNDAY in days
    
    def is_weekday_scheduled(self) -> bool:
        """Check if weekday is scheduled"""
        days = self.get_days_of_week()
        return any(day in days for day in [self.MONDAY, self.TUESDAY, self.WEDNESDAY, self.THURSDAY, self.FRIDAY])
    
    def get_start_time_minutes(self) -> int:
        """Get start time in minutes from midnight"""
        hours, minutes = map(int, self.start_time.split(":"))
        return hours * 60 + minutes
    
    def get_end_time_minutes(self) -> int:
        """Get end time in minutes from midnight"""
        hours, minutes = map(int, self.end_time.split(":"))
        return hours * 60 + minutes
    
    def get_duration_minutes(self) -> int:
        """Get schedule duration in minutes"""
        start = self.get_start_time_minutes()
        end = self.get_end_time_minutes()
        if end >= start:
            return end - start
        else:  # Schedule crosses midnight
            return (24 * 60) - start + end
    
    def to_dict(self) -> dict:
        """Convert schedule to dictionary"""
        return {
            "id": self.id,
            "camera_id": self.camera_id,
            "days_of_week": self.get_days_of_week(),
            "start_time": self.start_time,
            "end_time": self.end_time,
            "record_type": self.record_type,
            "is_active": self.is_active == 1,
            "duration_minutes": self.get_duration_minutes(),
        }
