"""Recording service for video recording management"""
import os
import asyncio
from typing import Optional, List
from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.models.recording import Recording
from app.models.video_metadata import VideoMetadata
from app.config import settings


class RecordingService:
    """Recording management service"""
    
    def __init__(self, db: AsyncSession):
        """Initialize recording service
        
        Args:
            db: Database session
        """
        self.db = db
        self.active_recordings: dict = {}  # {camera_id: {process, file_path, started_at}}
    
    async def start_recording(
        self,
        camera_id: int,
        rtsp_url: str,
        recording_type: str = "motion",
        output_path: Optional[str] = None,
    ) -> Optional[Recording]:
        """Start recording for camera
        
        Args:
            camera_id: Camera ID
            rtsp_url: RTSP stream URL
            recording_type: Type of recording (continuous, motion, scheduled)
            output_path: Output file path
            
        Returns:
            Recording object or None
        """
        if camera_id in self.active_recordings:
            return None  # Already recording
        
        # Generate output path
        if output_path is None:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = os.path.join(
                settings.RECORDINGS_PATH,
                str(camera_id),
                datetime.utcnow().strftime("%Y-%m-%d"),
                f"recording_{timestamp}.mp4"
            )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Build FFmpeg command
        cmd = self._build_recording_command(rtsp_url, output_path)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            # Create recording in database
            recording = Recording(
                camera_id=camera_id,
                file_path=output_path,
                recording_type=recording_type,
                start_time=datetime.utcnow().isoformat(),
                end_time="",
            )
            
            self.db.add(recording)
            await self.db.commit()
            await self.db.refresh(recording)
            
            # Store active recording
            self.active_recordings[camera_id] = {
                "process": process,
                "file_path": output_path,
                "recording_id": recording.id,
                "started_at": datetime.utcnow().isoformat(),
            }
            
            return recording
            
        except Exception as e:
            print(f"Failed to start recording for camera {camera_id}: {e}")
            return None
    
    def _build_recording_command(self, rtsp_url: str, output_path: str) -> list:
        """Build FFmpeg command for recording
        
        Args:
            rtsp_url: RTSP stream URL
            output_path: Output file path
            
        Returns:
            FFmpeg command as list
        """
        cmd = [
            settings.FFMPEG_PATH,
            "-i", rtsp_url,
            "-c:v", "libx264",
            "-preset", "medium",
            "-c:a", "aac",
            "-f", "segment",
            "-segment_time", str(settings.RECORDING_SEGMENT_DURATION_SECONDS),
            "-reset_timestamps", "1",
            "-strftime", "1",
            "-segment_format", "mp4",
            output_path,
        ]
        
        return cmd
    
    async def stop_recording(self, camera_id: int) -> Optional[Recording]:
        """Stop recording for camera
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Updated recording or None
        """
        if camera_id not in self.active_recordings:
            return None  # Not recording
        
        recording_info = self.active_recordings[camera_id]
        process = recording_info["process"]
        recording_id = recording_info["recording_id"]
        
        # Stop FFmpeg process
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
        
        # Update recording in database
        result = await self.db.execute(
            select(Recording).where(Recording.id == recording_id)
        )
        recording = result.scalar_one_or_none()
        
        if recording:
            recording.end_time = datetime.utcnow().isoformat()
            
            # Get file size and duration
            try:
                file_size = os.path.getsize(recording.file_path)
                recording.file_size = file_size
                
                # Calculate duration
                start = datetime.fromisoformat(recording.start_time)
                end = datetime.fromisoformat(recording.end_time)
                recording.duration = int((end - start).total_seconds())
                
            except Exception:
                pass
            
            await self.db.commit()
            await self.db.refresh(recording)
        
        # Remove from active recordings
        del self.active_recordings[camera_id]
        
        return recording
    
    def is_recording(self, camera_id: int) -> bool:
        """Check if camera is recording
        
        Args:
            camera_id: Camera ID
            
        Returns:
            True if recording
        """
        return camera_id in self.active_recordings
    
    async def get_recordings(
        self,
        camera_id: Optional[int] = None,
        recording_type: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Recording]:
        """Get recordings with filtering
        
        Args:
            camera_id: Filter by camera
            recording_type: Filter by type
            start_date: Start date filter
            end_date: End date filter
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of recordings
        """
        query = select(Recording)
        
        if camera_id is not None:
            query = query.where(Recording.camera_id == camera_id)
        
        if recording_type is not None:
            query = query.where(Recording.recording_type == recording_type)
        
        if start_date is not None:
            query = query.where(Recording.start_time >= start_date)
        
        if end_date is not None:
            query = query.where(Recording.end_time <= end_date)
        
        query = query.order_by(Recording.start_time.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_recording(self, recording_id: int) -> Optional[Recording]:
        """Get recording by ID
        
        Args:
            recording_id: Recording ID
            
        Returns:
            Recording or None
        """
        result = await self.db.execute(
            select(Recording).where(Recording.id == recording_id)
        )
        return result.scalar_one_or_none()
    
    async def delete_recording(self, recording_id: int) -> bool:
        """Delete recording
        
        Args:
            recording_id: Recording ID
            
        Returns:
            True if deleted
        """
        recording = await self.get_recording(recording_id)
        if not recording:
            return False
        
        # Delete file
        try:
            if os.path.exists(recording.file_path):
                os.remove(recording.file_path)
        except Exception:
            pass
        
        # Delete from database
        await self.db.delete(recording)
        await self.db.commit()
        
        return True
    
    async def export_recording(
        self,
        recording_id: int,
        output_path: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
    ) -> bool:
        """Export recording segment
        
        Args:
            recording_id: Recording ID
            output_path: Output file path
            start_time: Start time for export
            end_time: End time for export
            
        Returns:
            True if exported successfully
        """
        recording = await self.get_recording(recording_id)
        if not recording:
            return False
        
        from app.utils.video import VideoProcessor
        processor = VideoProcessor()
        
        start = start_time or recording.start_time
        duration = None
        
        if end_time:
            start_dt = datetime.fromisoformat(start)
            end_dt = datetime.fromisoformat(end_time)
            duration = str(int((end_dt - start_dt).total_seconds()))
        
        return await processor.cut_video(
            recording.file_path,
            output_path,
            start,
            duration,
        )
    
    async def get_recording_metadata(
        self,
        recording_id: int,
    ) -> Optional[VideoMetadata]:
        """Get recording metadata
        
        Args:
            recording_id: Recording ID
            
        Returns:
            VideoMetadata or None
        """
        result = await self.db.execute(
            select(VideoMetadata).where(VideoMetadata.recording_id == recording_id)
        )
        return result.scalar_one_or_none()
    
    async def get_active_recordings(self) -> List[dict]:
        """Get list of active recordings
        
        Returns:
            List of active recording info
        """
        return [
            {
                "camera_id": camera_id,
                "recording_id": info["recording_id"],
                "file_path": info["file_path"],
                "started_at": info["started_at"],
            }
            for camera_id, info in self.active_recordings.items()
        ]


# Global recording service instance
_recording_service: Optional[RecordingService] = None


def get_recording_service(db: AsyncSession) -> RecordingService:
    """Get or create recording service instance
    
    Args:
        db: Database session
        
    Returns:
        RecordingService instance
    """
    global _recording_service
    if _recording_service is None:
        _recording_service = RecordingService(db)
    return _recording_service


# Convenience functions
async def start_recording(
    camera_id: int,
    rtsp_url: str,
    db: AsyncSession,
    recording_type: str = "motion",
    output_path: Optional[str] = None,
) -> Optional[Recording]:
    """Start recording"""
    service = get_recording_service(db)
    return await service.start_recording(camera_id, rtsp_url, recording_type, output_path)


async def stop_recording(
    camera_id: int,
    db: AsyncSession,
) -> Optional[Recording]:
    """Stop recording"""
    service = get_recording_service(db)
    return await service.stop_recording(camera_id)


async def get_recordings(
    db: AsyncSession,
    camera_id: Optional[int] = None,
    recording_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Recording]:
    """Get recordings"""
    service = get_recording_service(db)
    return await service.get_recordings(
        camera_id, recording_type, start_date, end_date, skip, limit
    )


async def export_recording(
    recording_id: int,
    output_path: str,
    db: AsyncSession,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
) -> bool:
    """Export recording"""
    service = get_recording_service(db)
    return await service.export_recording(recording_id, output_path, start_time, end_time)
