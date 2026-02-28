"""Camera service for managing IP cameras"""
from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.utils.rtsp import test_rtsp_connection, validate_rtsp_url
from app.utils.onvif import discover_cameras, get_camera_info


class CameraService:
    """Camera management service"""
    
    def __init__(self, db: AsyncSession):
        """Initialize camera service
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_camera(
        self,
        name: str,
        rtsp_url: str,
        onvif_host: Optional[str] = None,
        onvif_port: Optional[int] = None,
        onvif_username: Optional[str] = None,
        onvif_password: Optional[str] = None,
        recording_mode: str = "motion",
        detection_enabled: bool = True,
        detection_confidence: float = 0.5,
    ) -> Camera:
        """Create a new camera
        
        Args:
            name: Camera name
            rtsp_url: RTSP stream URL
            onvif_host: ONVIF host
            onvif_port: ONVIF port
            onvif_username: ONVIF username
            onvif_password: ONVIF password
            recording_mode: Recording mode
            detection_enabled: Enable AI detection
            detection_confidence: Detection confidence threshold
            
        Returns:
            Created camera
        """
        camera = Camera(
            name=name,
            rtsp_url=rtsp_url,
            onvif_host=onvif_host,
            onvif_port=onvif_port,
            onvif_username=onvif_username,
            onvif_password=onvif_password,
            recording_mode=recording_mode,
            detection_enabled=1 if detection_enabled else 0,
            detection_confidence=detection_confidence,
            status="offline",
        )
        
        self.db.add(camera)
        await self.db.commit()
        await self.db.refresh(camera)
        
        return camera
    
    async def get_camera(self, camera_id: int) -> Optional[Camera]:
        """Get camera by ID
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Camera or None
        """
        result = await self.db.execute(
            select(Camera).where(Camera.id == camera_id)
        )
        return result.scalar_one_or_none()
    
    async def list_cameras(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Camera]:
        """List cameras with optional filtering
        
        Args:
            status: Filter by status
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of cameras
        """
        query = select(Camera)
        
        if status:
            query = query.where(Camera.status == status)
        
        query = query.offset(skip).limit(limit)
        query = query.order_by(Camera.name)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update_camera(
        self,
        camera_id: int,
        name: Optional[str] = None,
        rtsp_url: Optional[str] = None,
        onvif_host: Optional[str] = None,
        onvif_port: Optional[int] = None,
        onvif_username: Optional[str] = None,
        onvif_password: Optional[str] = None,
        recording_mode: Optional[str] = None,
        detection_enabled: Optional[bool] = None,
        detection_confidence: Optional[float] = None,
    ) -> Optional[Camera]:
        """Update camera
        
        Args:
            camera_id: Camera ID
            name: New name
            rtsp_url: New RTSP URL
            onvif_host: New ONVIF host
            onvif_port: New ONVIF port
            onvif_username: New ONVIF username
            onvif_password: New ONVIF password
            recording_mode: New recording mode
            detection_enabled: New detection enabled flag
            detection_confidence: New detection confidence
            
        Returns:
            Updated camera or None
        """
        camera = await self.get_camera(camera_id)
        if not camera:
            return None
        
        if name is not None:
            camera.name = name
        if rtsp_url is not None:
            camera.rtsp_url = rtsp_url
        if onvif_host is not None:
            camera.onvif_host = onvif_host
        if onvif_port is not None:
            camera.onvif_port = onvif_port
        if onvif_username is not None:
            camera.onvif_username = onvif_username
        if onvif_password is not None:
            camera.onvif_password = onvif_password
        if recording_mode is not None:
            camera.recording_mode = recording_mode
        if detection_enabled is not None:
            camera.detection_enabled = 1 if detection_enabled else 0
        if detection_confidence is not None:
            camera.detection_confidence = detection_confidence
        
        camera.updated_at = datetime.utcnow().isoformat()
        
        await self.db.commit()
        await self.db.refresh(camera)
        
        return camera
    
    async def update_camera_status(
        self,
        camera_id: int,
        status: str,
        resolution_width: Optional[int] = None,
        resolution_height: Optional[int] = None,
        codec: Optional[str] = None,
        fps: Optional[int] = None,
    ) -> Optional[Camera]:
        """Update camera status
        
        Args:
            camera_id: Camera ID
            status: New status (online, offline, error)
            resolution_width: Resolution width
            resolution_height: Resolution height
            codec: Video codec
            fps: Frames per second
            
        Returns:
            Updated camera or None
        """
        camera = await self.get_camera(camera_id)
        if not camera:
            return None
        
        camera.status = status
        
        if resolution_width is not None:
            camera.resolution_width = resolution_width
        if resolution_height is not None:
            camera.resolution_height = resolution_height
        if codec is not None:
            camera.codec = codec
        if fps is not None:
            camera.fps = fps
        
        camera.updated_at = datetime.utcnow().isoformat()
        
        await self.db.commit()
        await self.db.refresh(camera)
        
        return camera
    
    async def delete_camera(self, camera_id: int) -> bool:
        """Delete camera
        
        Args:
            camera_id: Camera ID
            
        Returns:
            True if deleted
        """
        camera = await self.get_camera(camera_id)
        if not camera:
            return False
        
        await self.db.delete(camera)
        await self.db.commit()
        
        return True
    
    async def test_connection(
        self,
        camera_id: int,
    ) -> Tuple[bool, str, Optional[dict]]:
        """Test camera connection
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Tuple of (success, message, stream_info)
        """
        camera = await self.get_camera(camera_id)
        if not camera:
            return False, "Camera not found", None
        
        # Extract credentials from RTSP URL
        from app.utils.rtsp import extract_rtsp_credentials
        username, password = extract_rtsp_credentials(camera.rtsp_url)
        
        success, message, stream_info = await test_rtsp_connection(
            camera.rtsp_url,
            username,
            password,
            timeout=10,
        )
        
        # Update camera status
        if success:
            await self.update_camera_status(
                camera_id,
                "online",
                resolution_width=stream_info.get("width") if stream_info else None,
                resolution_height=stream_info.get("height") if stream_info else None,
                codec=stream_info.get("codec") if stream_info else None,
                fps=stream_info.get("fps") if stream_info else None,
            )
        else:
            await self.update_camera_status(camera_id, "error")
        
        return success, message, stream_info
    
    async def discover_cameras(
        self,
        ip_range: Optional[str] = None,
        port: int = 80,
    ) -> List[dict]:
        """Discover ONVIF cameras on network
        
        Args:
            ip_range: IP range to scan
            port: ONVIF port
            
        Returns:
            List of discovered cameras
        """
        cameras = await discover_cameras(ip_range, port, timeout=5)
        
        return [
            {
                "ip": camera.ip,
                "port": camera.port,
                "name": camera.name,
                "manufacturer": camera.manufacturer,
                "model": camera.model,
                "rtsp_url": camera.rtsp_url,
                "onvif_url": camera.onvif_url,
            }
            for camera in cameras
        ]
    
    async def get_camera_count(self) -> int:
        """Get total camera count
        
        Returns:
            Number of cameras
        """
        result = await self.db.execute(select(func.count(Camera.id)))
        return result.scalar() or 0
    
    async def get_online_camera_count(self) -> int:
        """Get online camera count
        
        Returns:
            Number of online cameras
        """
        result = await self.db.execute(
            select(func.count(Camera.id)).where(Camera.status == "online")
        )
        return result.scalar() or 0


# Convenience functions
async def add_camera(
    name: str,
    rtsp_url: str,
    db: AsyncSession,
    **kwargs,
) -> Camera:
    """Add a new camera"""
    service = CameraService(db)
    return await service.create_camera(name, rtsp_url, **kwargs)


async def update_camera(
    camera_id: int,
    db: AsyncSession,
    **kwargs,
) -> Optional[Camera]:
    """Update camera"""
    service = CameraService(db)
    return await service.update_camera(camera_id, **kwargs)


async def delete_camera(camera_id: int, db: AsyncSession) -> bool:
    """Delete camera"""
    service = CameraService(db)
    return await service.delete_camera(camera_id)


async def get_camera(camera_id: int, db: AsyncSession) -> Optional[Camera]:
    """Get camera by ID"""
    service = CameraService(db)
    return await service.get_camera(camera_id)


async def list_cameras(
    db: AsyncSession,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Camera]:
    """List cameras"""
    service = CameraService(db)
    return await service.list_cameras(status, skip, limit)


async def test_camera_connection(
    camera_id: int,
    db: AsyncSession,
) -> Tuple[bool, str, Optional[dict]]:
    """Test camera connection"""
    service = CameraService(db)
    return await service.test_connection(camera_id)
