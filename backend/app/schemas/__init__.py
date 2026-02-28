"""Pydantic schemas for API validation and serialization"""
from app.schemas.common import (
    PaginatedResponse,
    MessageResponse,
    ErrorResponse,
    HealthResponse,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    TokenResponse,
)
from app.schemas.camera import (
    CameraBase,
    CameraCreate,
    CameraUpdate,
    CameraResponse,
    CameraStatusUpdate,
    CameraDiscoveryResponse,
)
from app.schemas.recording import (
    RecordingBase,
    RecordingCreate,
    RecordingUpdate,
    RecordingResponse,
    RecordingExportRequest,
    RecordingExportResponse,
)
from app.schemas.event import (
    EventBase,
    EventCreate,
    EventUpdate,
    EventResponse,
    EventAcknowledgeRequest,
    EventFilter,
)
from app.schemas.setting import (
    SettingBase,
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    SettingCategory,
)

__all__ = [
    # Common
    "PaginatedResponse",
    "MessageResponse",
    "ErrorResponse",
    "HealthResponse",
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "TokenResponse",
    # Camera
    "CameraBase",
    "CameraCreate",
    "CameraUpdate",
    "CameraResponse",
    "CameraStatusUpdate",
    "CameraDiscoveryResponse",
    # Recording
    "RecordingBase",
    "RecordingCreate",
    "RecordingUpdate",
    "RecordingResponse",
    "RecordingExportRequest",
    "RecordingExportResponse",
    # Event
    "EventBase",
    "EventCreate",
    "EventUpdate",
    "EventResponse",
    "EventAcknowledgeRequest",
    "EventFilter",
    # Setting
    "SettingBase",
    "SettingCreate",
    "SettingUpdate",
    "SettingResponse",
    "SettingCategory",
]
