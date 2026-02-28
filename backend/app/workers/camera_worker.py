"""Camera worker for monitoring camera status"""
import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.models.event import Event
from app.config import settings


class CameraWorker:
    """Background worker for camera monitoring"""
    
    def __init__(self, db: AsyncSession):
        """Initialize camera worker
        
        Args:
            db: Database session
        """
        self.db = db
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start camera monitoring worker"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._monitor_cameras())
    
    async def stop(self) -> None:
        """Stop camera monitoring worker"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_cameras(self) -> None:
        """Monitor camera status periodically"""
        while self._running:
            try:
                await self._check_camera_status()
                await asyncio.sleep(settings.CAMERA_MONITOR_INTERVAL)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Camera worker error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    async def _check_camera_status(self) -> None:
        """Check status of all cameras"""
        result = await self.db.execute(
            select(Camera).where(Camera.status == "online")
        )
        online_cameras = list(result.scalars().all())
        
        for camera in online_cameras:
            try:
                # Test connection
                from app.utils.rtsp import test_rtsp_connection
                success, message, stream_info = await test_rtsp_connection(
                    camera.rtsp_url,
                    camera.onvif_username,
                    camera.onvif_password,
                    timeout=10,
                )
                
                if not success:
                    # Camera went offline
                    await self._handle_camera_offline(camera, message)
                else:
                    # Update stream info
                    await self._update_camera_stream_info(camera, stream_info)
            
            except Exception as e:
                print(f"Error checking camera {camera.id}: {e}")
    
    async def _handle_camera_offline(self, camera: Camera, error_message: str) -> None:
        """Handle camera going offline
        
        Args:
            camera: Camera object
            error_message: Error message
        """
        # Update camera status
        camera.status = "offline"
        camera.updated_at = datetime.utcnow().isoformat()
        await self.db.commit()
        
        # Create event
        event = Event(
            event_type=Event.EVENT_TYPE_CAMERA_OFFLINE,
            camera_id=camera.id,
            details={"error": error_message},
            timestamp=datetime.utcnow().isoformat(),
            status="new",
        )
        
        self.db.add(event)
        await self.db.commit()
        
        # Send notification
        from app.services.notification_service import notification_service
        await notification_service.send_camera_offline_notification(
            camera.name,
            datetime.utcnow().isoformat(),
        )
    
    async def _update_camera_stream_info(
        self,
        camera: Camera,
        stream_info: Optional[dict],
    ) -> None:
        """Update camera stream information
        
        Args:
            camera: Camera object
            stream_info: Stream information from ffprobe
        """
        if not stream_info:
            return
        
        camera.resolution_width = stream_info.get("width")
        camera.resolution_height = stream_info.get("height")
        camera.codec = stream_info.get("codec")
        camera.fps = stream_info.get("fps")
        camera.updated_at = datetime.utcnow().isoformat()
        
        await self.db.commit()
