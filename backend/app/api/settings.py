"""Settings API endpoints"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.setting import (
    SettingResponse,
    SettingCreate,
    SettingUpdate,
    SettingCategory,
    BulkSettingsUpdate,
    StorageSettings,
    RecordingSettings,
    DetectionSettings,
    NotificationSettings,
    SystemSettings,
    AuthSettings,
)
from app.schemas.common import MessageResponse
from app.models.setting import Setting
from app.api.deps import get_current_user, require_admin
from app.models.user import User
from app.services.logging_metrics import logging_metrics_service

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("", response_model=List[SettingResponse])
async def list_settings(
    category: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """List all settings with optional category filter
    
    Args:
        category: Filter by category
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of settings
    """
    from sqlalchemy import select
    
    query = select(Setting)
    
    if category:
        query = query.where(Setting.category == category)
    
    query = query.order_by(Setting.key)
    
    result = await db.execute(query)
    settings = list(result.scalars().all())
    
    return [s.to_dict() for s in settings]


@router.get("/categories", response_model=List[SettingCategory])
async def list_setting_categories(
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """List settings grouped by category
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of setting categories
    """
    from sqlalchemy import select
    
    result = await db.execute(select(Setting))
    all_settings = list(result.scalars().all())
    
    # Group by category
    categories = {}
    for setting in all_settings:
        cat = setting.category
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(setting.to_dict())
    
    return [
        {
            "name": cat,
            "description": cat.title(),
            "settings": categories[cat],
        }
        for cat in categories.keys()
    ]


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get setting by key
    
    Args:
        key: Setting key
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Setting value
        
    Raises:
        HTTPException: If setting not found
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(Setting).where(Setting.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found",
        )
    
    return setting.to_dict()


@router.post("", response_model=SettingResponse, status_code=status.HTTP_201_CREATED)
async def create_setting(
    setting_data: SettingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Create a new setting
    
    Args:
        setting_data: Setting creation data
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Created setting
        
    Raises:
        HTTPException: If setting key already exists
    """
    from sqlalchemy import select
    
    # Check if setting exists
    result = await db.execute(
        select(Setting).where(Setting.key == setting_data.key)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Setting with this key already exists",
        )
    
    setting = Setting(
        key=setting_data.key,
        value=str(setting_data.value),
        category=setting_data.category,
        description=setting_data.description,
    )
    
    db.add(setting)
    await db.commit()
    await db.refresh(setting)
    
    return setting.to_dict()


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    setting_data: SettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> dict:
    """Update setting value
    
    Args:
        key: Setting key
        setting_data: Setting update data
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Updated setting
        
    Raises:
        HTTPException: If setting not found
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(Setting).where(Setting.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found",
        )
    
    setting.set_value(setting_data.value)
    if setting_data.description:
        setting.description = setting_data.description
    
    await db.commit()
    await db.refresh(setting)
    
    return setting.to_dict()


@router.delete("/{key}", response_model=MessageResponse)
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> MessageResponse:
    """Delete setting
    
    Args:
        key: Setting key
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If setting not found
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(Setting).where(Setting.key == key)
    )
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Setting not found",
        )
    
    await db.delete(setting)
    await db.commit()
    
    return MessageResponse(message="Setting deleted successfully")


@router.post("/bulk", response_model=MessageResponse)
async def bulk_update_settings(
    update_data: BulkSettingsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> MessageResponse:
    """Bulk update settings
    
    Args:
        update_data: Dictionary of settings to update
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Success message
    """
    from sqlalchemy import select
    
    for key, value in update_data.settings.items():
        result = await db.execute(
            select(Setting).where(Setting.key == key)
        )
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.set_value(value)
        await db.commit()
    
    return MessageResponse(
        message=f"Updated {len(update_data.settings)} settings"
    )


@router.get("/storage", response_model=StorageSettings)
async def get_storage_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> StorageSettings:
    """Get storage settings
    
    Returns:
        Storage settings
    """
    from sqlalchemy import select
    
    settings_dict = {}
    result = await db.execute(
        select(Setting).where(Setting.category == "storage")
    )
    storage_settings = list(result.scalars().all())
    
    for s in storage_settings:
        settings_dict[s.key] = s.get_value()
    
    return StorageSettings(
        retention_days=settings_dict.get("storage.retention_days", 30),
        max_disk_usage_gb=settings_dict.get("storage.max_disk_usage_gb", 1000),
        auto_cleanup=settings_dict.get("storage.auto_cleanup", True),
        cleanup_threshold_percent=settings_dict.get("storage.cleanup_threshold_percent", 90),
    )


@router.get("/recording", response_model=RecordingSettings)
async def get_recording_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecordingSettings:
    """Get recording settings
    
    Returns:
        Recording settings
    """
    from sqlalchemy import select
    
    settings_dict = {}
    result = await db.execute(
        select(Setting).where(Setting.category == "recording")
    )
    recording_settings = list(result.scalars().all())
    
    for s in recording_settings:
        settings_dict[s.key] = s.get_value()
    
    return RecordingSettings(
        segment_duration_seconds=settings_dict.get("recording.segment_duration_seconds", 300),
        motion_pre_buffer_seconds=settings_dict.get("recording.motion_pre_buffer_seconds", 5),
        motion_post_buffer_seconds=settings_dict.get("recording.motion_post_buffer_seconds", 5),
        continuous_fps=settings_dict.get("recording.continuous_fps", 15),
        motion_fps=settings_dict.get("recording.motion_fps", 15),
        scheduled_fps=settings_dict.get("recording.scheduled_fps", 15),
    )


@router.get("/detection", response_model=DetectionSettings)
async def get_detection_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DetectionSettings:
    """Get detection settings
    
    Returns:
        Detection settings
    """
    from sqlalchemy import select
    
    settings_dict = {}
    result = await db.execute(
        select(Setting).where(Setting.category == "detection")
    )
    detection_settings = list(result.scalars().all())
    
    for s in detection_settings:
        settings_dict[s.key] = s.get_value()
    
    return DetectionSettings(
        enabled=settings_dict.get("detection.enabled", True),
        confidence_threshold=settings_dict.get("detection.confidence_threshold", 0.5),
        interval_seconds=settings_dict.get("detection.interval_seconds", 1),
        model=settings_dict.get("detection.model", "yolov8n"),
        detect_person=settings_dict.get("detection.detect_person", True),
        detect_vehicle=settings_dict.get("detection.detect_vehicle", False),
        detect_animal=settings_dict.get("detection.detect_animal", False),
    )


@router.get("/notification", response_model=NotificationSettings)
async def get_notification_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> NotificationSettings:
    """Get notification settings
    
    Returns:
        Notification settings
    """
    from sqlalchemy import select
    
    settings_dict = {}
    result = await db.execute(
        select(Setting).where(Setting.category == "notification")
    )
    notification_settings = list(result.scalars().all())
    
    for s in notification_settings:
        settings_dict[s.key] = s.get_value()
    
    return NotificationSettings(
        telegram_enabled=settings_dict.get("notification.telegram_enabled", False),
        telegram_bot_token=settings_dict.get("notification.telegram_bot_token", ""),
        telegram_chat_id=settings_dict.get("notification.telegram_chat_id", ""),
        notify_on_motion=settings_dict.get("notification.notify_on_motion", True),
        notify_on_person=settings_dict.get("notification.notify_on_person", True),
        notify_on_camera_offline=settings_dict.get("notification.notify_on_camera_offline", True),
        notify_on_storage_full=settings_dict.get("notification.notify_on_storage_full", True),
    )


@router.get("/system", response_model=SystemSettings)
async def get_system_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SystemSettings:
    """Get system settings
    
    Returns:
        System settings
    """
    from sqlalchemy import select
    
    settings_dict = {}
    result = await db.execute(
        select(Setting).where(Setting.category == "system")
    )
    system_settings = list(result.scalars().all())
    
    for s in system_settings:
        settings_dict[s.key] = s.get_value()
    
    return SystemSettings(
        debug_mode=settings_dict.get("system.debug_mode", False),
        log_level=settings_dict.get("system.log_level", "INFO"),
        timezone=settings_dict.get("system.timezone", "UTC"),
        max_websocket_connections=settings_dict.get("system.max_websocket_connections", 100),
        rate_limit_enabled=settings_dict.get("system.rate_limit_enabled", True),
        rate_limit_requests_per_minute=settings_dict.get("system.rate_limit_requests_per_minute", 60),
    )


@router.get("/auth", response_model=AuthSettings)
async def get_auth_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AuthSettings:
    """Get authentication settings
    
    Returns:
        Authentication settings
    """
    from sqlalchemy import select
    
    settings_dict = {}
    result = await db.execute(
        select(Setting).where(Setting.category == "auth")
    )
    auth_settings = list(result.scalars().all())
    
    for s in auth_settings:
        settings_dict[s.key] = s.get_value()
    
    return AuthSettings(
        session_timeout_minutes=settings_dict.get("auth.session_timeout_minutes", 30),
        max_login_attempts=settings_dict.get("auth.max_login_attempts", 5),
        lockout_duration_minutes=settings_dict.get("auth.lockout_duration_minutes", 15),
        require_strong_password=settings_dict.get("auth.require_strong_password", True),
        password_min_length=settings_dict.get("auth.password_min_length", 8),
    )


# Logging metrics endpoints

@router.get("/logging/metrics")
async def get_logging_metrics(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get logging system metrics
    
    Returns:
        Logging metrics including disk usage, file count, error statistics
    """
    return logging_metrics_service.get_metrics()


@router.get("/logging/files")
async def get_logging_files(
    category: Optional[str] = Query(None, description="Filter by log category (backend, ai, system, security, audit)"),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """Get information about log files
    
    Args:
        category: Optional filter by log category
        
    Returns:
        List of log files with metadata
    """
    return logging_metrics_service.get_files_info(category)


@router.get("/logging/categories")
async def get_logging_category_metrics(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get metrics grouped by log category
    
    Returns:
        Metrics for each log category
    """
    return logging_metrics_service.get_category_metrics()


@router.get("/logging/health")
async def get_logging_health(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get logging system health status
    
    Returns:
        Health status and metrics
    """
    return logging_metrics_service.get_health_status()


@router.get("/logging/errors")
async def get_logging_error_statistics(
    hours: int = Query(24, ge=1, le=168, description="Period in hours for error statistics"),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get error statistics for logging
    
    Args:
        hours: Period in hours (1-168)
        
    Returns:
        Error statistics
    """
    return logging_metrics_service.get_error_statistics(hours)


@router.post("/logging/cleanup", response_model=MessageResponse)
async def cleanup_logging(
    max_age_days: Optional[int] = Query(None, ge=1, le=365, description="Maximum age of logs in days"),
    current_user: User = Depends(require_admin),
) -> MessageResponse:
    """Clean up old log files
    
    Args:
        max_age_days: Maximum age of logs in days (default from settings)
        
    Returns:
        Cleanup result
    """
    result = logging_metrics_service.cleanup_logs(max_age_days)
    return MessageResponse(
        message=f"Deleted {result['deleted_count']} log files older than {result['max_age_days']} days"
    )
