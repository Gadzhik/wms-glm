"""User model for authentication and authorization"""
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.camera import Camera


class User(Base):
    """User model for storing user accounts"""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="viewer",
        server_default="viewer"
    )
    refresh_token: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat()
    )
    last_login: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('admin', 'viewer')", name="check_users_role"),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', role='{self.role}')>"
    
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == "admin"
    
    def is_viewer(self) -> bool:
        """Check if user has viewer role"""
        return self.role == "viewer"
    
    def to_dict(self) -> dict:
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at,
            "last_login": self.last_login,
        }
