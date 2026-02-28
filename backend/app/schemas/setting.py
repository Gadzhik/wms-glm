"""Setting-related Pydantic schemas"""
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class SettingBase(BaseModel):
    """Base setting schema"""
    key: str = Field(..., min_length=1, max_length=100, description="Setting key")
    value: Any = Field(..., description="Setting value")
    category: str = Field(
        ...,
        pattern="^(storage|recording|detection|notification|system|auth)$",
        description="Setting category"
    )
    description: Optional[str] = Field(None, max_length=500, description="Setting description")


class SettingCreate(SettingBase):
    """Schema for creating a new setting"""
    pass


class SettingUpdate(BaseModel):
    """Schema for updating a setting"""
    value: Any = Field(..., description="New setting value")
    description: Optional[str] = Field(None, max_length=500, description="Setting description")


class SettingResponse(BaseModel):
    """Schema for setting response"""
    model_config = ConfigDict(from_attributes=True)
    
    key: str = Field(..., description="Setting key")
    value: Any = Field(..., description="Setting value")
    category: str = Field(..., description="Setting category")
    description: Optional[str] = Field(None, description="Setting description")
    updated_at: str = Field(..., description="Last update timestamp")


class SettingCategory(BaseModel):
    """Schema for setting category"""
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    settings: list[SettingResponse] = Field(default_factory=list, description="Settings in this category")


class StorageSettings(BaseModel):
    """Storage settings"""
    retention_days: int = Field(default=30, ge=1, le=365, description="Retention period in days")
    max_disk_usage_gb: int = Field(default=1000, ge=10, description="Maximum disk usage in GB")
    auto_cleanup: bool = Field(default=True, description="Enable automatic cleanup")
    cleanup_threshold_percent: int = Field(default=90, ge=50, le=99, description="Cleanup threshold percentage")


class RecordingSettings(BaseModel):
    """Recording settings"""
    segment_duration_seconds: int = Field(default=300, ge=60, le=3600, description="Segment duration in seconds")
    motion_pre_buffer_seconds: int = Field(default=5, ge=0, le=60, description="Motion pre-buffer in seconds")
    motion_post_buffer_seconds: int = Field(default=5, ge=0, le=60, description="Motion post-buffer in seconds")
    continuous_fps: int = Field(default=15, ge=1, le=60, description="Continuous recording FPS")
    motion_fps: int = Field(default=15, ge=1, le=60, description="Motion recording FPS")
    scheduled_fps: int = Field(default=15, ge=1, le=60, description="Scheduled recording FPS")


class DetectionSettings(BaseModel):
    """AI detection settings"""
    enabled: bool = Field(default=True, description="Enable AI detection")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Detection confidence threshold")
    interval_seconds: int = Field(default=1, ge=1, le=10, description="Detection interval in seconds")
    model: str = Field(default="yolov8n", description="YOLO model name")
    detect_person: bool = Field(default=True, description="Detect persons")
    detect_vehicle: bool = Field(default=False, description="Detect vehicles")
    detect_animal: bool = Field(default=False, description="Detect animals")


class NotificationSettings(BaseModel):
    """Notification settings"""
    telegram_enabled: bool = Field(default=False, description="Enable Telegram notifications")
    telegram_bot_token: Optional[str] = Field(None, description="Telegram bot token")
    telegram_chat_id: Optional[str] = Field(None, description="Telegram chat ID")
    notify_on_motion: bool = Field(default=True, description="Notify on motion detection")
    notify_on_person: bool = Field(default=True, description="Notify on person detection")
    notify_on_camera_offline: bool = Field(default=True, description="Notify on camera offline")
    notify_on_storage_full: bool = Field(default=True, description="Notify on storage full")


class SystemSettings(BaseModel):
    """System settings"""
    debug_mode: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$", description="Log level")
    timezone: str = Field(default="UTC", description="System timezone")
    max_websocket_connections: int = Field(default=100, ge=1, description="Maximum WebSocket connections")
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(default=60, ge=1, description="Rate limit requests per minute")


class AuthSettings(BaseModel):
    """Authentication settings"""
    session_timeout_minutes: int = Field(default=30, ge=5, le=1440, description="Session timeout in minutes")
    max_login_attempts: int = Field(default=5, ge=1, le=20, description="Maximum login attempts")
    lockout_duration_minutes: int = Field(default=15, ge=1, le=1440, description="Lockout duration in minutes")
    require_strong_password: bool = Field(default=True, description="Require strong password")
    password_min_length: int = Field(default=8, ge=6, le=32, description="Minimum password length")


class BulkSettingsUpdate(BaseModel):
    """Schema for bulk settings update"""
    settings: dict[str, Any] = Field(..., description="Dictionary of settings to update")


class SettingsExport(BaseModel):
    """Schema for settings export"""
    settings: list[SettingResponse] = Field(..., description="List of all settings")
    exported_at: datetime = Field(default_factory=datetime.utcnow, description="Export timestamp")
    version: str = Field(default="1.0.0", description="Settings version")


class SettingsImport(BaseModel):
    """Schema for settings import"""
    settings: list[SettingCreate] = Field(..., description="List of settings to import")
    overwrite: bool = Field(default=False, description="Overwrite existing settings")
