"""Common Pydantic schemas for API responses"""
from typing import Generic, TypeVar, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Standard message response"""
    message: str = Field(..., description="Response message")
    success: bool = Field(default=True, description="Success status")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status (healthy/unhealthy)")
    version: str = Field(..., description="Application version")
    database: str = Field(..., description="Database connection status")
    redis: str = Field(..., description="Redis connection status")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check timestamp")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")
    has_next: bool = Field(..., description="Whether there is a next page")
    has_previous: bool = Field(..., description="Whether there is a previous page")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse[T]":
        """Create a paginated response"""
        total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_previous=page > 1,
        )


class IdResponse(BaseModel):
    """Response with ID only"""
    id: int = Field(..., description="Created/Updated resource ID")


class CountResponse(BaseModel):
    """Response with count"""
    count: int = Field(..., description="Count of items")


class FileResponse(BaseModel):
    """File response"""
    filename: str = Field(..., description="File name")
    content_type: str = Field(..., description="Content type")
    size: int = Field(..., description="File size in bytes")
    url: str = Field(..., description="File URL")


class ExportResponse(BaseModel):
    """Export response"""
    export_id: str = Field(..., description="Export ID")
    status: str = Field(..., description="Export status")
    url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(None, description="URL expiration time")


class WebSocketMessage(BaseModel):
    """WebSocket message"""
    type: str = Field(..., description="Message type")
    data: Any = Field(..., description="Message data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class StreamMetadata(BaseModel):
    """Live stream metadata"""
    camera_id: int = Field(..., description="Camera ID")
    stream_url: str = Field(..., description="Stream URL")
    hls_playlist: str = Field(..., description="HLS playlist URL")
    status: str = Field(..., description="Stream status")
    viewers: int = Field(default=0, description="Current number of viewers")
    resolution: Optional[str] = Field(None, description="Stream resolution")
    fps: Optional[int] = Field(None, description="Stream FPS")
    bitrate: Optional[int] = Field(None, description="Stream bitrate in kbps")


class SystemStats(BaseModel):
    """System statistics"""
    cpu_usage: float = Field(..., description="CPU usage percentage")
    memory_usage: float = Field(..., description="Memory usage percentage")
    disk_usage: float = Field(..., description="Disk usage percentage")
    disk_free_gb: float = Field(..., description="Free disk space in GB")
    uptime_seconds: int = Field(..., description="System uptime in seconds")
    active_cameras: int = Field(..., description="Number of active cameras")
    active_streams: int = Field(..., description="Number of active streams")
    pending_events: int = Field(..., description="Number of pending events")
