"""API endpoints"""
from app.api.deps import get_current_user, get_current_active_user, require_admin
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.cameras import router as cameras_router
from app.api.recordings import router as recordings_router
from app.api.events import router as events_router
from app.api.streams import router as streams_router
from app.api.settings import router as settings_router

__all__ = [
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "require_admin",
    # Routers
    "auth_router",
    "users_router",
    "cameras_router",
    "recordings_router",
    "events_router",
    "streams_router",
    "settings_router",
]
