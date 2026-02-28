"""Streams API endpoints for live streaming"""
from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.common import StreamMetadata, MessageResponse
from app.services.stream_service import stream_service
from app.api.deps import get_current_user
from app.models.user import User
from app.core.websocket import manager

router = APIRouter(prefix="/streams", tags=["Streams"])


@router.get("/{camera_id}", response_model=StreamMetadata)
async def get_stream_metadata(
    camera_id: int,
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get live stream metadata for camera
    
    Args:
        camera_id: Camera ID
        current_user: Current authenticated user
        
    Returns:
        Stream metadata
        
    Raises:
        HTTPException: If camera is not streaming
    """
    if not stream_service.is_streaming(camera_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Stream not active for this camera",
        )
    
    stream_info = stream_service.get_stream_info(camera_id)
    
    return {
        "camera_id": camera_id,
        "stream_url": stream_info["playlist_url"],
        "hls_playlist": stream_info["playlist_url"],
        "status": "streaming",
        "viewers": manager.get_camera_subscriber_count(camera_id),
        "resolution": "1280x720",  # Default resolution
        "fps": 15,  # Default FPS
        "bitrate": 1000,  # Default bitrate in kbps
    }


@router.post("/{camera_id}/start", response_model=MessageResponse)
async def start_stream(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Start live stream for camera
    
    Args:
        camera_id: Camera ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If camera not found or stream already active
    """
    from app.models.camera import Camera
    from sqlalchemy import select
    
    result = await db.execute(
        select(Camera).where(Camera.id == camera_id)
    )
    camera = result.scalar_one_or_none()
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )
    
    if stream_service.is_streaming(camera_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stream already active for this camera",
        )
    
    success = await stream_service.start_stream(camera_id, camera.rtsp_url)
    
    if success:
        return MessageResponse(message="Stream started successfully")
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start stream",
        )


@router.post("/{camera_id}/stop", response_model=MessageResponse)
async def stop_stream(
    camera_id: int,
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Stop live stream for camera
    
    Args:
        camera_id: Camera ID
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    success = await stream_service.stop_stream(camera_id)
    
    if success:
        return MessageResponse(message="Stream stopped successfully")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stream not active for this camera",
        )


@router.get("", response_model=list)
async def list_active_streams(
    current_user: User = Depends(get_current_user),
) -> list:
    """List all active streams
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        List of active stream metadata
    """
    return stream_service.get_active_streams()


@router.websocket("/{camera_id}/ws")
async def websocket_stream(
    websocket: WebSocket,
    camera_id: int,
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """WebSocket endpoint for live streaming
    
    Args:
        websocket: WebSocket connection
        camera_id: Camera ID
        token: JWT token for authentication
        db: Database session
        
    Raises:
        HTTPException: If authentication fails
    """
    from app.core.security import verify_token
    
    # Verify token
    payload = verify_token(token)
    if not payload or payload.get("type") != "access":
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    user_id = int(payload.get("sub"))
    
    # Accept connection
    connection_id = await manager.connect(websocket, user_id)
    await manager.subscribe_camera(connection_id, camera_id)
    
    try:
        # Send stream metadata
        stream_info = stream_service.get_stream_info(camera_id)
        if stream_info:
            await websocket.send_json({
                "type": "stream_info",
                "data": stream_info,
            })
        
        # Keep connection alive
        while True:
            data = await websocket.receive_text()
            
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            elif data == "stop":
                break
    
    except WebSocketDisconnect:
        pass
    
    finally:
        await manager.unsubscribe_camera(connection_id)
        await manager.disconnect(connection_id, "Client disconnected")
