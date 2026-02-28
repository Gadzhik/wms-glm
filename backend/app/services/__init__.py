"""Business logic services"""
from app.services.auth_service import (
    AuthService,
    authenticate_user,
    create_user,
    verify_token,
)
from app.services.camera_service import (
    CameraService,
    add_camera,
    update_camera,
    delete_camera,
    get_camera,
    list_cameras,
    test_camera_connection,
)
from app.services.stream_service import (
    StreamService,
    start_stream,
    stop_stream,
    get_stream_url,
    create_hls_stream,
)
from app.services.recording_service import (
    RecordingService,
    start_recording,
    stop_recording,
    get_recordings,
    export_recording,
)
from app.services.storage_service import (
    StorageService,
    cleanup_old_files,
    get_disk_usage,
    check_storage_space,
)
from app.services.detection_service import (
    DetectionService,
    detect_persons,
    process_frame,
)
from app.services.notification_service import (
    NotificationService,
    send_notification,
    send_telegram_notification,
)
from app.services.schedule_service import (
    ScheduleService,
    create_schedule,
    update_schedule,
    delete_schedule,
    get_schedules,
    check_schedule,
)
from app.services.llm_bridge import (
    LLMBridge,
    get_llm_bridge,
    initialize_llm_bridge,
    shutdown_llm_bridge,
)

__all__ = [
    # Auth
    "AuthService",
    "authenticate_user",
    "create_user",
    "verify_token",
    # Camera
    "CameraService",
    "add_camera",
    "update_camera",
    "delete_camera",
    "get_camera",
    "list_cameras",
    "test_camera_connection",
    # Stream
    "StreamService",
    "start_stream",
    "stop_stream",
    "get_stream_url",
    "create_hls_stream",
    # Recording
    "RecordingService",
    "start_recording",
    "stop_recording",
    "get_recordings",
    "export_recording",
    # Storage
    "StorageService",
    "cleanup_old_files",
    "get_disk_usage",
    "check_storage_space",
    # Detection
    "DetectionService",
    "detect_persons",
    "process_frame",
    # Notification
    "NotificationService",
    "send_notification",
    "send_telegram_notification",
    # Schedule
    "ScheduleService",
    "create_schedule",
    "update_schedule",
    "delete_schedule",
    "get_schedules",
    "check_schedule",
    # LLM
    "LLMBridge",
    "get_llm_bridge",
    "initialize_llm_bridge",
    "shutdown_llm_bridge",
]
