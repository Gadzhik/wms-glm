"""Camera-related Pydantic schemas"""
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl, ConfigDict, field_validator


class CameraBase(BaseModel):
    """Base camera schema"""
    name: str = Field(..., min_length=1, max_length=100, description="Camera name")
    rtsp_url: str = Field(..., max_length=500, description="RTSP stream URL")
    onvif_host: Optional[str] = Field(None, max_length=100, description="ONVIF host")
    onvif_port: Optional[int] = Field(None, ge=1, le=65535, description="ONVIF port")
    onvif_username: Optional[str] = Field(None, max_length=50, description="ONVIF username")
    onvif_password: Optional[str] = Field(None, max_length=100, description="ONVIF password")
    recording_mode: str = Field(
        default="motion",
        pattern="^(continuous|motion|scheduled)$",
        description="Recording mode"
    )
    detection_enabled: bool = Field(default=True, description="Enable AI detection")
    detection_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Detection confidence threshold"
    )


class CameraCreate(CameraBase):
    """Schema for creating a new camera"""
    pass


class CameraUpdate(BaseModel):
    """Schema for updating a camera"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Camera name")
    rtsp_url: Optional[str] = Field(None, max_length=500, description="RTSP stream URL")
    onvif_host: Optional[str] = Field(None, max_length=100, description="ONVIF host")
    onvif_port: Optional[int] = Field(None, ge=1, le=65535, description="ONVIF port")
    onvif_username: Optional[str] = Field(None, max_length=50, description="ONVIF username")
    onvif_password: Optional[str] = Field(None, max_length=100, description="ONVIF password")
    recording_mode: Optional[str] = Field(
        None,
        pattern="^(continuous|motion|scheduled)$",
        description="Recording mode"
    )
    detection_enabled: Optional[bool] = Field(None, description="Enable AI detection")
    detection_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Detection confidence threshold"
    )


class CameraResponse(BaseModel):
    """Schema for camera response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="Camera ID")
    name: str = Field(..., description="Camera name")
    rtsp_url: str = Field(..., description="RTSP stream URL (masked)")
    onvif_host: Optional[str] = Field(None, description="ONVIF host")
    onvif_port: Optional[int] = Field(None, description="ONVIF port")
    onvif_username: Optional[str] = Field(None, description="ONVIF username")
    onvif_password: Optional[str] = Field(None, description="ONVIF password (masked)")
    status: str = Field(..., description="Camera status")
    recording_mode: str = Field(..., description="Recording mode")
    detection_enabled: bool = Field(..., description="AI detection enabled")
    detection_confidence: float = Field(..., description="Detection confidence threshold")
    resolution_width: Optional[int] = Field(None, description="Resolution width")
    resolution_height: Optional[int] = Field(None, description="Resolution height")
    codec: Optional[str] = Field(None, description="Video codec")
    fps: Optional[int] = Field(None, description="Frames per second")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")
    
    @field_validator("rtsp_url", mode="before")
    @classmethod
    def mask_rtsp_url(cls, v: str) -> str:
        """Mask RTSP URL in response"""
        if v and "@" in v:
            protocol, rest = v.split("://", 1)
            if "@" in rest:
                return f"{protocol}://***@{rest.split('@')[1]}"
        return "***" if v else ""


class CameraStatusUpdate(BaseModel):
    """Schema for updating camera status"""
    status: str = Field(..., pattern="^(online|offline|error)$", description="Camera status")


class CameraDiscoveryRequest(BaseModel):
    """Schema for camera discovery request"""
    ip_range: Optional[str] = Field(None, description="IP range to scan (e.g., 192.168.1.0/24)")
    port: Optional[int] = Field(default=80, ge=1, le=65535, description="ONVIF port")
    timeout: Optional[int] = Field(default=5, ge=1, le=60, description="Discovery timeout in seconds")


class DiscoveredCamera(BaseModel):
    """Schema for a discovered camera"""
    ip: str = Field(..., description="Camera IP address")
    port: int = Field(..., description="Camera port")
    name: Optional[str] = Field(None, description="Camera name")
    manufacturer: Optional[str] = Field(None, description="Camera manufacturer")
    model: Optional[str] = Field(None, description="Camera model")
    rtsp_url: Optional[str] = Field(None, description="RTSP URL")
    onvif_url: Optional[str] = Field(None, description="ONVIF URL")


class CameraDiscoveryResponse(BaseModel):
    """Schema for camera discovery response"""
    cameras: list[DiscoveredCamera] = Field(..., description="List of discovered cameras")
    total: int = Field(..., description="Total number of cameras found")
    scan_duration: float = Field(..., description="Scan duration in seconds")


class CameraTestRequest(BaseModel):
    """Schema for testing camera connection"""
    rtsp_url: str = Field(..., description="RTSP URL to test")
    username: Optional[str] = Field(None, description="Username for authentication")
    password: Optional[str] = Field(None, description="Password for authentication")
    timeout: Optional[int] = Field(default=10, ge=1, le=60, description="Connection timeout in seconds")


class CameraTestResponse(BaseModel):
    """Schema for camera test response"""
    success: bool = Field(..., description="Connection successful")
    message: str = Field(..., description="Test result message")
    resolution: Optional[str] = Field(None, description="Detected resolution")
    codec: Optional[str] = Field(None, description="Detected codec")
    fps: Optional[int] = Field(None, description="Detected FPS")
    latency_ms: Optional[float] = Field(None, description="Connection latency in milliseconds")
