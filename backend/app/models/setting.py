"""Setting model for system settings"""
from datetime import datetime

from sqlalchemy import String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Setting(Base):
    """Setting model for storing system settings"""
    
    __tablename__ = "settings"
    
    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    updated_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat()
    )
    
    # Category constants
    CATEGORY_STORAGE = "storage"
    CATEGORY_RECORDING = "recording"
    CATEGORY_DETECTION = "detection"
    CATEGORY_NOTIFICATION = "notification"
    CATEGORY_SYSTEM = "system"
    CATEGORY_AUTH = "auth"
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "category IN ('storage', 'recording', 'detection', 'notification', 'system', 'auth')",
            name="check_settings_category"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Setting(key='{self.key}', category='{self.category}')>"
    
    def is_storage_setting(self) -> bool:
        """Check if this is a storage setting"""
        return self.category == self.CATEGORY_STORAGE
    
    def is_recording_setting(self) -> bool:
        """Check if this is a recording setting"""
        return self.category == self.CATEGORY_RECORDING
    
    def is_detection_setting(self) -> bool:
        """Check if this is a detection setting"""
        return self.category == self.CATEGORY_DETECTION
    
    def is_notification_setting(self) -> bool:
        """Check if this is a notification setting"""
        return self.category == self.CATEGORY_NOTIFICATION
    
    def is_system_setting(self) -> bool:
        """Check if this is a system setting"""
        return self.category == self.CATEGORY_SYSTEM
    
    def is_auth_setting(self) -> bool:
        """Check if this is an auth setting"""
        return self.category == self.CATEGORY_AUTH
    
    def get_value(self) -> any:
        """Parse and return setting value"""
        import json
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value
    
    def set_value(self, value: any) -> None:
        """Set setting value"""
        import json
        if isinstance(value, (dict, list)):
            self.value = json.dumps(value)
        elif isinstance(value, bool):
            self.value = "true" if value else "false"
        elif isinstance(value, (int, float)):
            self.value = str(value)
        else:
            self.value = value
    
    def to_dict(self) -> dict:
        """Convert setting to dictionary"""
        return {
            "key": self.key,
            "value": self.get_value(),
            "category": self.category,
            "description": self.description,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def create(cls, key: str, value: any, category: str, description: str | None = None) -> "Setting":
        """Create a new setting"""
        setting = cls(
            key=key,
            category=category,
            description=description
        )
        setting.set_value(value)
        return setting
