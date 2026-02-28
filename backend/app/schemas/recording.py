"""Recording-related Pydantic schemas"""
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class RecordingBase(BaseModel):
    """Base recording schema"""
    camera_id: int = Field(..., gt=0, description="Camera ID")
    recording_type: str = Field(
        default="motion",
        pattern="^(continuous|motion|scheduled)$",
        description="Recording type"
    )
    start_time: str = Field(..., description="Start time (ISO 8601)")
    end_time: str = Field(..., description="End time (ISO 8601)")


class RecordingCreate(RecordingBase):
    """Schema for creating a new recording"""
    file_path: str = Field(..., max_length=500, description="File path")
    is_encrypted: bool = Field(default=False, description="Is recording encrypted")
    codec: Optional[str] = Field(None, max_length=20, description="Video codec")
    resolution_width: Optional[int] = Field(None, gt=0, description="Resolution width")
    resolution_height: Optional[int] = Field(None, gt=0, description="Resolution height")
    bitrate: Optional[int] = Field(None, gt=0, description="Bitrate in kbps")


class RecordingUpdate(BaseModel):
    """Schema for updating a recording"""
    end_time: Optional[str] = Field(None, description="End time (ISO 8601)")
    file_size: Optional[int] = Field(None, ge=0, description="File size in bytes")
    duration: Optional[int] = Field(None, ge=0, description="Duration in seconds")
    is_encrypted: Optional[bool] = Field(None, description="Is recording encrypted")
    encryption_key: Optional[str] = Field(None, max_length=255, description="Encryption key")
    codec: Optional[str] = Field(None, max_length=20, description="Video codec")
    resolution_width: Optional[int] = Field(None, gt=0, description="Resolution width")
    resolution_height: Optional[int] = Field(None, gt=0, description="Resolution height")
    bitrate: Optional[int] = Field(None, gt=0, description="Bitrate in kbps")


class RecordingResponse(BaseModel):
    """Schema for recording response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Recording ID")
    camera_id: int = Field(..., description="Camera ID")
    file_path: str = Field(..., description="File path")
    recording_type: str = Field(..., description="Recording type")
    start_time: str = Field(..., description="Start time (ISO 8601)")
    end_time: str = Field(..., description="End time (ISO 8601)")
    file_size: int = Field(..., description="File size in bytes")
    file_size_mb: float = Field(..., description="File size in megabytes")
    duration: int = Field(..., description="Duration in seconds")
    duration_minutes: float = Field(..., description="Duration in minutes")
    is_encrypted: bool = Field(..., description="Is recording encrypted")
    codec: Optional[str] = Field(None, description="Video codec")
    resolution_width: Optional[int] = Field(None, description="Resolution width")
    resolution_height: Optional[int] = Field(None, description="Resolution height")
    bitrate: Optional[int] = Field(None, description="Bitrate in kbps")
    created_at: str = Field(..., description="Creation timestamp")


class RecordingFilter(BaseModel):
    """Schema for recording filter"""
    camera_id: Optional[int] = Field(None, gt=0, description="Filter by camera ID")
    recording_type: Optional[str] = Field(
        None,
        pattern="^(continuous|motion|scheduled)$",
        description="Filter by recording type"
    )
    start_date: Optional[str] = Field(None, description="Start date (ISO 8601)")
    end_date: Optional[str] = Field(None, description="End date (ISO 8601)")
    min_duration: Optional[int] = Field(None, ge=0, description="Minimum duration in seconds")
    max_duration: Optional[int] = Field(None, ge=0, description="Maximum duration in seconds")


class RecordingExportRequest(BaseModel):
    """Schema for recording export request"""
    recording_ids: list[int] = Field(..., min_length=1, description="List of recording IDs to export")
    format: str = Field(
        default="mp4",
        pattern="^(mp4|avi|mkv|mov)$",
        description="Export format"
    )
    include_metadata: bool = Field(default=True, description="Include metadata in export")
    quality: Optional[str] = Field(
        None,
        pattern="^(low|medium|high|original)$",
        description="Export quality"
    )
    start_time: Optional[str] = Field(None, description="Custom start time (ISO 8601)")
    end_time: Optional[str] = Field(None, description="Custom end time (ISO 8601)")


class RecordingExportResponse(BaseModel):
    """Schema for recording export response"""
    export_id: str = Field(..., description="Export ID")
    status: str = Field(..., description="Export status")
    progress: float = Field(..., ge=0.0, le=100.0, description="Export progress percentage")
    file_url: Optional[str] = Field(None, description="Download URL when ready")
    file_size: Optional[int] = Field(None, description="Exported file size in bytes")
    expires_at: Optional[datetime] = Field(None, description="URL expiration time")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Export creation time")


class RecordingMetadata(BaseModel):
    """Schema for recording metadata"""
    recording_id: int = Field(..., description="Recording ID")
    thumbnails: list[str] = Field(default_factory=list, description="List of thumbnail paths")
    detected_objects: list[dict] = Field(default_factory=list, description="List of detected objects")
    motion_events: list[dict] = Field(default_factory=list, description="List of motion events")
    person_count: int = Field(default=0, description="Number of detected persons")


class RecordingStats(BaseModel):
    """Schema for recording statistics"""
    total_recordings: int = Field(..., description="Total number of recordings")
    total_duration_seconds: int = Field(..., description="Total duration in seconds")
    total_size_bytes: int = Field(..., description="Total size in bytes")
    by_type: dict[str, int] = Field(default_factory=dict, description="Count by recording type")
    by_camera: dict[int, int] = Field(default_factory=dict, description="Count by camera")
    oldest_recording: Optional[str] = Field(None, description="Oldest recording timestamp")
    newest_recording: Optional[str] = Field(None, description="Newest recording timestamp")
