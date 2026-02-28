"""Cameras API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.camera import (
    CameraCreate,
    CameraUpdate,
    CameraResponse,
    CameraStatusUpdate,
    CameraDiscoveryResponse,
    CameraTestRequest,
    CameraTestResponse,
)
from app.schemas.common import MessageResponse
from app.services.camera_service import CameraService
from app.api.deps import get_current_user, get_pagination
from app.models.user import User

router = APIRouter(prefix="/cameras", tags=["Cameras"])


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def create_camera(
    camera_data: CameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Create a new camera
    
    Args:
        camera_data: Camera creation data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Created camera
    """
    service = CameraService(db)
    camera = await service.create_camera(
        name=camera_data.name,
        rtsp_url=camera_data.rtsp_url,
        onvif_host=camera_data.onvif_host,
        onvif_port=camera_data.onvif_port,
        onvif_username=camera_data.onvif_username,
        onvif_password=camera_data.onvif_password,
        recording_mode=camera_data.recording_mode,
        detection_enabled=camera_data.detection_enabled,
        detection_confidence=camera_data.detection_confidence,
    )
    
    return camera.to_dict(include_sensitive=False)


@router.get("", response_model=List[CameraResponse])
async def list_cameras(
    status_filter: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """List all cameras
    
    Args:
        status_filter: Filter by camera status
        skip: Number of records to skip
        limit: Maximum number of records
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of cameras
    """
    service = CameraService(db)
    cameras = await service.list_cameras(
        status=status_filter,
        skip=skip,
        limit=limit,
    )
    
    return [c.to_dict(include_sensitive=False) for c in cameras]


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get camera by ID
    
    Args:
        camera_id: Camera ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Camera information
        
    Raises:
        HTTPException: If camera not found
    """
    service = CameraService(db)
    camera = await service.get_camera(camera_id)
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )
    
    return camera.to_dict(include_sensitive=False)


@router.put("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: int,
    camera_data: CameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Update camera information
    
    Args:
        camera_id: Camera ID
        camera_data: Camera update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated camera
        
    Raises:
        HTTPException: If camera not found
    """
    service = CameraService(db)
    camera = await service.update_camera(camera_id, **camera_data.model_dump(exclude_unset=True))
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )
    
    return camera.to_dict(include_sensitive=False)


@router.delete("/{camera_id}", response_model=MessageResponse)
async def delete_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Delete camera
    
    Args:
        camera_id: Camera ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If camera not found
    """
    service = CameraService(db)
    success = await service.delete_camera(camera_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )
    
    return MessageResponse(message="Camera deleted successfully")


@router.post("/{camera_id}/status", response_model=CameraResponse)
async def update_camera_status(
    camera_id: int,
    status_data: CameraStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Update camera status
    
    Args:
        camera_id: Camera ID
        status_data: Status update data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Updated camera
        
    Raises:
        HTTPException: If camera not found
    """
    service = CameraService(db)
    camera = await service.update_camera_status(camera_id, status_data.status)
    
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Camera not found",
        )
    
    return camera.to_dict(include_sensitive=False)


@router.post("/{camera_id}/test", response_model=CameraTestResponse)
async def test_camera(
    camera_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CameraTestResponse:
    """Test camera connection
    
    Args:
        camera_id: Camera ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Test result
    """
    service = CameraService(db)
    success, message, stream_info = await service.test_connection(camera_id)
    
    return CameraTestResponse(
        success=success,
        message=message,
        resolution=f"{stream_info.get('width')}x{stream_info.get('height')}" if stream_info else None,
        codec=stream_info.get("codec") if stream_info else None,
        fps=stream_info.get("fps") if stream_info else None,
    )


@router.post("/discover", response_model=CameraDiscoveryResponse)
async def discover_cameras(
    ip_range: str = None,
    port: int = 80,
    current_user: User = Depends(get_current_user),
) -> CameraDiscoveryResponse:
    """Discover ONVIF cameras on network
    
    Args:
        ip_range: IP range to scan
        port: ONVIF port
        current_user: Current authenticated user
        
    Returns:
        Discovered cameras
    """
    service = CameraService(db)
    cameras = await service.discover_cameras(ip_range, port)
    
    return CameraDiscoveryResponse(
        cameras=cameras,
        total=len(cameras),
        scan_duration=5.0,
    )
