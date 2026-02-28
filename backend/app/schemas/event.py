"""Event-related Pydantic schemas"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class EventBase(BaseModel):
    """Base event schema"""
    event_type: str = Field(
        ...,
        pattern="^(motion_detected|person_detected|camera_offline|camera_error|storage_full|system_error)$",
        description="Event type"
    )
    camera_id: Optional[int] = Field(None, gt=0, description="Camera ID")
    recording_id: Optional[int] = Field(None, gt=0, description="Recording ID")
    details: Optional[dict] = Field(None, description="Additional event details")


class EventCreate(EventBase):
    """Schema for creating a new event"""
    pass


class EventUpdate(BaseModel):
    """Schema for updating an event"""
    status: Optional[str] = Field(
        None,
        pattern="^(new|acknowledged|resolved)$",
        description="Event status"
    )
    push_sent: Optional[bool] = Field(None, description="Push notification sent")
    details: Optional[dict] = Field(None, description="Additional event details")


class EventResponse(BaseModel):
    """Schema for event response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Event ID")
    event_type: str = Field(..., description="Event type")
    camera_id: Optional[int] = Field(None, description="Camera ID")
    recording_id: Optional[int] = Field(None, description="Recording ID")
    timestamp: str = Field(..., description="Event timestamp (ISO 8601)")
    details: Optional[dict] = Field(None, description="Additional event details")
    status: str = Field(..., description="Event status")
    push_sent: bool = Field(..., description="Push notification sent")


class EventAcknowledgeRequest(BaseModel):
    """Schema for acknowledging events"""
    event_ids: list[int] = Field(..., min_length=1, description="List of event IDs to acknowledge")
    note: Optional[str] = Field(None, max_length=500, description="Acknowledgment note")


class EventFilter(BaseModel):
    """Schema for event filter"""
    event_type: Optional[str] = Field(
        None,
        pattern="^(motion_detected|person_detected|camera_offline|camera_error|storage_full|system_error)$",
        description="Filter by event type"
    )
    camera_id: Optional[int] = Field(None, gt=0, description="Filter by camera ID")
    status: Optional[str] = Field(
        None,
        pattern="^(new|acknowledged|resolved)$",
        description="Filter by status"
    )
    start_date: Optional[str] = Field(None, description="Start date (ISO 8601)")
    end_date: Optional[str] = Field(None, description="End date (ISO 8601)")
    push_sent: Optional[bool] = Field(None, description="Filter by push sent status")


class EventStats(BaseModel):
    """Schema for event statistics"""
    total_events: int = Field(..., description="Total number of events")
    by_type: dict[str, int] = Field(default_factory=dict, description="Count by event type")
    by_status: dict[str, int] = Field(default_factory=dict, description="Count by status")
    by_camera: dict[int, int] = Field(default_factory=dict, description="Count by camera")
    new_events: int = Field(..., description="Number of new events")
    acknowledged_events: int = Field(..., description="Number of acknowledged events")
    resolved_events: int = Field(..., description="Number of resolved events")
    oldest_event: Optional[str] = Field(None, description="Oldest event timestamp")
    newest_event: Optional[str] = Field(None, description="Newest event timestamp")


class PersonDetectionEvent(BaseModel):
    """Schema for person detection event details"""
    timestamp: str = Field(..., description="Detection timestamp")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence")
    bbox: dict[str, int] = Field(..., description="Bounding box (x, y, width, height)")
    tracking_id: Optional[int] = Field(None, description="Tracking ID")


class MotionDetectionEvent(BaseModel):
    """Schema for motion detection event details"""
    timestamp: str = Field(..., description="Detection timestamp")
    level: float = Field(..., ge=0.0, le=1.0, description="Motion level")
    region: Optional[dict[str, int]] = Field(None, description="Motion region (x, y, width, height)")
    area_percentage: Optional[float] = Field(None, ge=0.0, le=100.0, description="Motion area percentage")


class CameraOfflineEvent(BaseModel):
    """Schema for camera offline event details"""
    offline_since: str = Field(..., description="Camera offline since timestamp")
    last_online: str = Field(..., description="Last online timestamp")
    reason: Optional[str] = Field(None, description="Offline reason")


class CameraErrorEvent(BaseModel):
    """Schema for camera error event details"""
    error_code: Optional[str] = Field(None, description="Error code")
    error_message: str = Field(..., description="Error message")
    error_type: Optional[str] = Field(None, description="Error type")


class StorageFullEvent(BaseModel):
    """Schema for storage full event details"""
    disk_usage_gb: float = Field(..., ge=0.0, description="Disk usage in GB")
    disk_total_gb: float = Field(..., ge=0.0, description="Total disk space in GB")
    threshold_gb: float = Field(..., ge=0.0, description="Threshold in GB")
