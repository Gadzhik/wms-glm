"""Log model for system logs"""
from datetime import datetime

from sqlalchemy import String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Log(Base):
    """Log model for storing system logs"""
    
    __tablename__ = "logs"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    component: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat(),
        index=True
    )
    
    # Log level constants
    LEVEL_DEBUG = "DEBUG"
    LEVEL_INFO = "INFO"
    LEVEL_WARNING = "WARNING"
    LEVEL_ERROR = "ERROR"
    LEVEL_CRITICAL = "CRITICAL"
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "level IN ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')",
            name="check_logs_level"
        ),
    )
    
    def __repr__(self) -> str:
        return f"<Log(id={self.id}, level='{self.level}', component='{self.component}')>"
    
    def is_debug(self) -> bool:
        """Check if log level is DEBUG"""
        return self.level == self.LEVEL_DEBUG
    
    def is_info(self) -> bool:
        """Check if log level is INFO"""
        return self.level == self.LEVEL_INFO
    
    def is_warning(self) -> bool:
        """Check if log level is WARNING"""
        return self.level == self.LEVEL_WARNING
    
    def is_error(self) -> bool:
        """Check if log level is ERROR"""
        return self.level == self.LEVEL_ERROR
    
    def is_critical(self) -> bool:
        """Check if log level is CRITICAL"""
        return self.level == self.LEVEL_CRITICAL
    
    def is_error_or_higher(self) -> bool:
        """Check if log level is ERROR or higher"""
        return self.level in (self.LEVEL_ERROR, self.LEVEL_CRITICAL)
    
    def get_details(self) -> dict:
        """Parse and return log details"""
        import json
        if self.details:
            try:
                return json.loads(self.details)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_details(self, details: dict) -> None:
        """Set log details from dictionary"""
        import json
        self.details = json.dumps(details)
    
    def to_dict(self) -> dict:
        """Convert log to dictionary"""
        return {
            "id": self.id,
            "level": self.level,
            "component": self.component,
            "message": self.message,
            "details": self.get_details(),
            "timestamp": self.timestamp,
        }
    
    @classmethod
    def create(cls, level: str, component: str, message: str, details: dict | None = None) -> "Log":
        """Create a new log entry"""
        log = cls(
            level=level,
            component=component,
            message=message
        )
        if details:
            log.set_details(details)
        return log
