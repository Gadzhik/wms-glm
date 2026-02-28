"""Recording worker for managing video recordings"""
import asyncio
from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.models.recording import Recording
from app.models.event import Event
from app.services.recording_service import get_recording_service
from app.services.schedule_service import ScheduleService
from app.config import settings


class RecordingWorker:
    """Background worker for recording management"""
    
    def __init__(self, db: AsyncSession):
        """Initialize recording worker
        
        Args:
            db: Database session
        """
        self.db = db
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start recording worker"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._manage_recordings())
    
    async def stop(self) -> None:
        """Stop recording worker"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _manage_recordings(self) -> None:
        """Manage recordings based on camera schedules and modes"""
        while self._running:
            try:
                await self._check_and_start_recordings()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Recording worker error: {e}")
                await asyncio.sleep(60)
    
    async def _check_and_start_recordings(self) -> None:
        """Check which cameras should be recording and start/stop recordings"""
        result = await self.db.execute(
            select(Camera).where(Camera.status == "online")
        )
        cameras = list(result.scalars().all())
        
        schedule_service = ScheduleService(self.db)
        recording_service = get_recording_service(self.db)
        
        for camera in cameras:
            try:
                # Check if should be recording based on schedule
                should_record = await self._should_camera_record(camera, schedule_service)
                
                is_recording = recording_service.is_recording(camera.id)
                
                if should_record and not is_recording:
                    # Start recording
                    await recording_service.start_recording(
                        camera.id,
                        camera.rtsp_url,
                        camera.recording_mode,
                    )
                    print(f"Started recording for camera {camera.id}")
                
                elif not should_record and is_recording:
                    # Stop recording
                    await recording_service.stop_recording(camera.id)
                    print(f"Stopped recording for camera {camera.id}")
            
            except Exception as e:
                print(f"Error managing recording for camera {camera.id}: {e}")
    
    async def _should_camera_record(
        self,
        camera: Camera,
        schedule_service: ScheduleService,
    ) -> bool:
        """Check if camera should be recording
        
        Args:
            camera: Camera object
            schedule_service: Schedule service
            
        Returns:
            True if should record
        """
        # Continuous recording
        if camera.recording_mode == "continuous":
            return True
        
        # Scheduled recording
        if camera.recording_mode == "scheduled":
            schedule = await schedule_service.check_schedule(camera.id)
            return schedule is not None
        
        # Motion recording (not implemented here, would need motion detection)
        if camera.recording_mode == "motion":
            return False  # Would need motion detection service
        
        return False
    
    async def stop_all_recordings(self) -> None:
        """Stop all active recordings"""
        recording_service = get_recording_service(self.db)
        active_recordings = await recording_service.get_active_recordings()
        
        for recording_info in active_recordings:
            camera_id = recording_info["camera_id"]
            await recording_service.stop_recording(camera_id)
            print(f"Stopped recording for camera {camera_id}")


async def start_recording_for_camera(
    camera_id: int,
    rtsp_url: str,
    recording_type: str,
    db: AsyncSession,
) -> Optional[Recording]:
    """Start recording for specific camera
    
    Args:
        camera_id: Camera ID
        rtsp_url: RTSP URL
        recording_type: Recording type
        db: Database session
        
    Returns:
        Recording object or None
    """
    recording_service = get_recording_service(db)
    return await recording_service.start_recording(camera_id, rtsp_url, recording_type)


async def stop_recording_for_camera(
    camera_id: int,
    db: AsyncSession,
) -> Optional[Recording]:
    """Stop recording for specific camera
    
    Args:
        camera_id: Camera ID
        db: Database session
        
    Returns:
        Recording object or None
    """
    recording_service = get_recording_service(db)
    return await recording_service.stop_recording(camera_id)
