"""Utility modules"""
from app.utils.rtsp import (
    RTSPClient,
    RTSPConnectionError,
    test_rtsp_connection,
)
from app.utils.onvif import (
    ONVIFClient,
    discover_cameras,
    get_camera_info,
)
from app.utils.video import (
    VideoProcessor,
    get_video_info,
    extract_frames,
    generate_thumbnail,
    transcode_video,
)
from app.utils.ai import (
    PersonDetector,
    detect_persons,
    load_yolo_model,
)

__all__ = [
    # RTSP
    "RTSPClient",
    "RTSPConnectionError",
    "test_rtsp_connection",
    # ONVIF
    "ONVIFClient",
    "discover_cameras",
    "get_camera_info",
    # Video
    "VideoProcessor",
    "get_video_info",
    "extract_frames",
    "generate_thumbnail",
    "transcode_video",
    # AI
    "PersonDetector",
    "detect_persons",
    "load_yolo_model",
]
