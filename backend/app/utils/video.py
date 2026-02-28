"""Video processing utilities using FFmpeg"""
import asyncio
import subprocess
import os
from typing import Optional, List, Dict, Any
from pathlib import Path


class VideoProcessor:
    """Video processor using FFmpeg"""
    
    def __init__(self, ffmpeg_path: str = "ffmpeg", ffprobe_path: str = "ffprobe"):
        """Initialize video processor
        
        Args:
            ffmpeg_path: Path to FFmpeg executable
            ffprobe_path: Path to FFprobe executable
        """
        self.ffmpeg_path = ffmpeg_path
        self.ffprobe_path = ffprobe_path
    
    async def get_video_info(self, video_path: str) -> Optional[Dict[str, Any]]:
        """Get video file information
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video info or None if failed
        """
        try:
            import json
            
            cmd = [
                self.ffprobe_path,
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path,
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                return self._parse_video_info(data)
            
            return None
            
        except Exception as e:
            return None
    
    def _parse_video_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse FFprobe output
        
        Args:
            data: FFprobe JSON output
            
        Returns:
            Parsed video info
        """
        info = {
            "format": data.get("format", {}),
            "streams": data.get("streams", []),
        }
        
        # Find video stream
        video_stream = None
        for stream in info["streams"]:
            if stream.get("codec_type") == "video":
                video_stream = stream
                break
        
        if video_stream:
            info["video"] = {
                "codec": video_stream.get("codec_name"),
                "width": video_stream.get("width"),
                "height": video_stream.get("height"),
                "fps": self._parse_fps(video_stream.get("r_frame_rate")),
                "bitrate": video_stream.get("bit_rate"),
                "duration": float(video_stream.get("duration", 0)),
            }
        
        # Find audio stream
        audio_stream = None
        for stream in info["streams"]:
            if stream.get("codec_type") == "audio":
                audio_stream = stream
                break
        
        if audio_stream:
            info["audio"] = {
                "codec": audio_stream.get("codec_name"),
                "sample_rate": audio_stream.get("sample_rate"),
                "channels": audio_stream.get("channels"),
            }
        
        return info
    
    def _parse_fps(self, fps_str: Optional[str]) -> Optional[float]:
        """Parse FPS string to float"""
        if not fps_str:
            return None
        
        if "/" in fps_str:
            num, den = fps_str.split("/")
            try:
                return float(num) / float(den)
            except (ValueError, ZeroDivisionError):
                return None
        
        try:
            return float(fps_str)
        except ValueError:
            return None
    
    async def generate_thumbnail(
        self,
        video_path: str,
        output_path: str,
        timestamp: str = "00:00:01",
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> bool:
        """Generate thumbnail from video
        
        Args:
            video_path: Path to video file
            output_path: Path for output thumbnail
            timestamp: Timestamp for thumbnail (default: 1 second)
            width: Optional width for thumbnail
            height: Optional height for thumbnail
            
        Returns:
            True if successful
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-ss", timestamp,
                "-vframes", "1",
            ]
            
            if width or height:
                scale = ""
                if width and height:
                    scale = f"{width}:{height}"
                elif width:
                    scale = f"{width}:-1"
                elif height:
                    scale = f"-1:{height}"
                cmd.extend(["-vf", f"scale={scale}"])
            
            cmd.extend(["-y", output_path])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            return process.returncode == 0 and os.path.exists(output_path)
            
        except Exception:
            return False
    
    async def extract_frames(
        self,
        video_path: str,
        output_dir: str,
        fps: float = 1.0,
        prefix: str = "frame",
    ) -> List[str]:
        """Extract frames from video
        
        Args:
            video_path: Path to video file
            output_dir: Directory for output frames
            fps: Frames per second to extract
            prefix: Filename prefix for frames
            
        Returns:
            List of extracted frame paths
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            cmd = [
                self.ffmpeg_path,
                "-i", video_path,
                "-vf", f"fps={fps}",
                f"{output_dir}/{prefix}_%04d.jpg",
                "-y",
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            # Get list of extracted frames
            frames = sorted(Path(output_dir).glob(f"{prefix}_*.jpg"))
            return [str(f) for f in frames]
            
        except Exception:
            return []
    
    async def transcode_video(
        self,
        input_path: str,
        output_path: str,
        codec: str = "libx264",
        bitrate: Optional[str] = None,
        fps: Optional[int] = None,
        resolution: Optional[str] = None,
        preset: str = "medium",
    ) -> bool:
        """Transcode video file
        
        Args:
            input_path: Path to input video
            output_path: Path for output video
            codec: Video codec
            bitrate: Target bitrate (e.g., "1M")
            fps: Target FPS
            resolution: Target resolution (e.g., "1280x720")
            preset: Encoding preset (ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow)
            
        Returns:
            True if successful
        """
        try:
            cmd = [self.ffmpeg_path, "-i", input_path]
            
            # Codec
            cmd.extend(["-c:v", codec])
            
            # Bitrate
            if bitrate:
                cmd.extend(["-b:v", bitrate])
            
            # FPS
            if fps:
                cmd.extend(["-r", str(fps)])
            
            # Resolution
            if resolution:
                cmd.extend(["-s", resolution])
            
            # Preset
            cmd.extend(["-preset", preset])
            
            # Audio codec
            cmd.extend(["-c:a", "aac"])
            
            # Output
            cmd.extend(["-y", output_path])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            return process.returncode == 0 and os.path.exists(output_path)
            
        except Exception:
            return False
    
    async def create_hls_stream(
        self,
        input_path: str,
        output_dir: str,
        segment_duration: int = 2,
    ) -> bool:
        """Create HLS stream from video
        
        Args:
            input_path: Path to input video
            output_dir: Directory for HLS output
            segment_duration: Segment duration in seconds
            
        Returns:
            True if successful
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            playlist_path = os.path.join(output_dir, "stream.m3u8")
            
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-c:v", "libx264",
                "-c:a", "aac",
                "-f", "hls",
                "-hls_time", str(segment_duration),
                "-hls_list_size", "0",
                "-hls_segment_filename", f"{output_dir}/segment_%03d.ts",
                playlist_path,
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            return process.returncode == 0 and os.path.exists(playlist_path)
            
        except Exception:
            return False
    
    async def cut_video(
        self,
        input_path: str,
        output_path: str,
        start_time: str,
        duration: Optional[str] = None,
    ) -> bool:
        """Cut video segment
        
        Args:
            input_path: Path to input video
            output_path: Path for output video
            start_time: Start time (HH:MM:SS or seconds)
            duration: Optional duration (HH:MM:SS or seconds)
            
        Returns:
            True if successful
        """
        try:
            cmd = [
                self.ffmpeg_path,
                "-i", input_path,
                "-ss", start_time,
            ]
            
            if duration:
                cmd.extend(["-t", duration])
            
            cmd.extend(["-c", "copy", "-y", output_path])
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            await process.communicate()
            
            return process.returncode == 0 and os.path.exists(output_path)
            
        except Exception:
            return False


async def get_video_info(video_path: str) -> Optional[Dict[str, Any]]:
    """Get video file information
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video info or None if failed
    """
    processor = VideoProcessor()
    return await processor.get_video_info(video_path)


async def extract_frames(
    video_path: str,
    output_dir: str,
    fps: float = 1.0,
    prefix: str = "frame",
) -> List[str]:
    """Extract frames from video
    
    Args:
        video_path: Path to video file
        output_dir: Directory for output frames
        fps: Frames per second to extract
        prefix: Filename prefix for frames
        
    Returns:
        List of extracted frame paths
    """
    processor = VideoProcessor()
    return await processor.extract_frames(video_path, output_dir, fps, prefix)


async def generate_thumbnail(
    video_path: str,
    output_path: str,
    timestamp: str = "00:00:01",
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> bool:
    """Generate thumbnail from video
    
    Args:
        video_path: Path to video file
        output_path: Path for output thumbnail
        timestamp: Timestamp for thumbnail
        width: Optional width for thumbnail
        height: Optional height for thumbnail
        
    Returns:
        True if successful
    """
    processor = VideoProcessor()
    return await processor.generate_thumbnail(video_path, output_path, timestamp, width, height)


async def transcode_video(
    input_path: str,
    output_path: str,
    codec: str = "libx264",
    bitrate: Optional[str] = None,
    fps: Optional[int] = None,
    resolution: Optional[str] = None,
    preset: str = "medium",
) -> bool:
    """Transcode video file
    
    Args:
        input_path: Path to input video
        output_path: Path for output video
        codec: Video codec
        bitrate: Target bitrate
        fps: Target FPS
        resolution: Target resolution
        preset: Encoding preset
        
    Returns:
        True if successful
    """
    processor = VideoProcessor()
    return await processor.transcode_video(
        input_path, output_path, codec, bitrate, fps, resolution, preset
    )
