"""Stream service for live streaming and HLS conversion"""
import asyncio
import os
from typing import Optional, Dict
from datetime import datetime

from app.config import settings
from app.utils.video import VideoProcessor


class StreamService:
    """Live streaming service"""
    
    def __init__(self):
        """Initialize stream service"""
        self.active_streams: Dict[int, Dict] = {}  # {camera_id: {process, output_dir, started_at}}
        self.video_processor = VideoProcessor(
            settings.FFMPEG_PATH,
            settings.FFPROBE_PATH,
        )
    
    async def start_stream(
        self,
        camera_id: int,
        rtsp_url: str,
        output_dir: Optional[str] = None,
    ) -> bool:
        """Start live stream for camera
        
        Args:
            camera_id: Camera ID
            rtsp_url: RTSP stream URL
            output_dir: Output directory for HLS segments
            
        Returns:
            True if stream started successfully
        """
        if camera_id in self.active_streams:
            return True  # Already streaming
        
        if output_dir is None:
            output_dir = os.path.join(settings.LIVE_STREAM_PATH, str(camera_id))
        
        os.makedirs(output_dir, exist_ok=True)
        
        playlist_path = os.path.join(output_dir, "stream.m3u8")
        
        # Build FFmpeg command for HLS streaming
        cmd = self._build_ffmpeg_command(rtsp_url, output_dir)
        
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            self.active_streams[camera_id] = {
                "process": process,
                "output_dir": output_dir,
                "playlist_path": playlist_path,
                "started_at": datetime.utcnow().isoformat(),
            }
            
            return True
            
        except Exception as e:
            print(f"Failed to start stream for camera {camera_id}: {e}")
            return False
    
    def _build_ffmpeg_command(self, rtsp_url: str, output_dir: str) -> list:
        """Build FFmpeg command for HLS streaming
        
        Args:
            rtsp_url: RTSP stream URL
            output_dir: Output directory
            
        Returns:
            FFmpeg command as list
        """
        cmd = [
            settings.FFMPEG_PATH,
            "-i", rtsp_url,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "zerolatency",
            "-c:a", "aac",
            "-b:v", f"{settings.LIVE_STREAM_BITRATE_KBPS}k",
            "-r", str(settings.LIVE_STREAM_FPS),
            "-s", settings.LIVE_STREAM_RESOLUTION,
            "-f", "hls",
            "-hls_time", str(settings.HLS_SEGMENT_DURATION),
            "-hls_list_size", "0",
            "-hls_segment_filename", os.path.join(output_dir, "segment_%03d.ts"),
            os.path.join(output_dir, "stream.m3u8"),
        ]
        
        # Add hardware acceleration if configured
        if settings.HARDWARE_ACCELERATION == "qsv":
            cmd.insert(1, "-hwaccel")
            cmd.insert(2, "qsv")
            cmd.insert(5, "-c:v")
            cmd.insert(6, "h264_qsv")
        elif settings.HARDWARE_ACCELERATION == "cuda":
            cmd.insert(1, "-hwaccel")
            cmd.insert(2, "cuda")
            cmd.insert(5, "-c:v")
            cmd.insert(6, "h264_nvenc")
        elif settings.HARDWARE_ACCELERATION == "vaapi":
            cmd.insert(1, "-hwaccel")
            cmd.insert(2, "vaapi")
            cmd.insert(5, "-c:v")
            cmd.insert(6, "h264_vaapi")
        
        return cmd
    
    async def stop_stream(self, camera_id: int) -> bool:
        """Stop live stream for camera
        
        Args:
            camera_id: Camera ID
            
        Returns:
            True if stream stopped
        """
        if camera_id not in self.active_streams:
            return False  # Not streaming
        
        stream_info = self.active_streams[camera_id]
        process = stream_info["process"]
        
        try:
            process.terminate()
            await asyncio.wait_for(process.wait(), timeout=5)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
        
        del self.active_streams[camera_id]
        return True
    
    def is_streaming(self, camera_id: int) -> bool:
        """Check if camera is streaming
        
        Args:
            camera_id: Camera ID
            
        Returns:
            True if streaming
        """
        return camera_id in self.active_streams
    
    def get_stream_url(self, camera_id: int) -> Optional[str]:
        """Get HLS playlist URL for camera
        
        Args:
            camera_id: Camera ID
            
        Returns:
            HLS playlist URL or None
        """
        if camera_id not in self.active_streams:
            return None
        
        stream_info = self.active_streams[camera_id]
        playlist_path = stream_info["playlist_path"]
        
        # Return relative path for serving via HTTP
        return f"/live/{camera_id}/stream.m3u8"
    
    def get_stream_info(self, camera_id: int) -> Optional[dict]:
        """Get stream information
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Stream info dict or None
        """
        if camera_id not in self.active_streams:
            return None
        
        stream_info = self.active_streams[camera_id]
        
        return {
            "camera_id": camera_id,
            "status": "streaming",
            "started_at": stream_info["started_at"],
            "playlist_url": self.get_stream_url(camera_id),
            "output_dir": stream_info["output_dir"],
        }
    
    def get_active_streams(self) -> list:
        """Get list of active streams
        
        Returns:
            List of active stream info
        """
        return [
            self.get_stream_info(camera_id)
            for camera_id in self.active_streams.keys()
        ]
    
    async def create_hls_stream(
        self,
        input_path: str,
        output_dir: str,
        segment_duration: int = 2,
    ) -> bool:
        """Create HLS stream from video file
        
        Args:
            input_path: Path to input video
            output_dir: Output directory
            segment_duration: Segment duration in seconds
            
        Returns:
            True if successful
        """
        return await self.video_processor.create_hls_stream(
            input_path, output_dir, segment_duration
        )
    
    async def cleanup_old_segments(
        self,
        camera_id: int,
        max_age_seconds: int = 300,
    ) -> int:
        """Cleanup old HLS segments
        
        Args:
            camera_id: Camera ID
            max_age_seconds: Maximum age of segments in seconds
            
        Returns:
            Number of files deleted
        """
        if camera_id not in self.active_streams:
            return 0
        
        stream_info = self.active_streams[camera_id]
        output_dir = stream_info["output_dir"]
        
        deleted_count = 0
        now = datetime.utcnow().timestamp()
        
        try:
            for filename in os.listdir(output_dir):
                if filename.endswith(".ts"):
                    filepath = os.path.join(output_dir, filename)
                    file_age = now - os.path.getmtime(filepath)
                    
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        deleted_count += 1
            
            return deleted_count
            
        except Exception as e:
            print(f"Failed to cleanup segments for camera {camera_id}: {e}")
            return deleted_count


# Global stream service instance
stream_service = StreamService()


# Convenience functions
async def start_stream(
    camera_id: int,
    rtsp_url: str,
    output_dir: Optional[str] = None,
) -> bool:
    """Start live stream"""
    return await stream_service.start_stream(camera_id, rtsp_url, output_dir)


async def stop_stream(camera_id: int) -> bool:
    """Stop live stream"""
    return await stream_service.stop_stream(camera_id)


def get_stream_url(camera_id: int) -> Optional[str]:
    """Get stream URL"""
    return stream_service.get_stream_url(camera_id)


async def create_hls_stream(
    input_path: str,
    output_dir: str,
    segment_duration: int = 2,
) -> bool:
    """Create HLS stream"""
    return await stream_service.create_hls_stream(input_path, output_dir, segment_duration)
