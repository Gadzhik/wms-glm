"""RTSP utilities for camera connection and streaming"""
import asyncio
import re
from typing import Optional, Tuple
from urllib.parse import urlparse


class RTSPConnectionError(Exception):
    """RTSP connection error"""
    pass


class RTSPClient:
    """RTSP client for connecting to IP cameras"""
    
    def __init__(
        self,
        rtsp_url: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 10,
    ):
        """Initialize RTSP client
        
        Args:
            rtsp_url: RTSP stream URL
            username: Optional username for authentication
            password: Optional password for authentication
            timeout: Connection timeout in seconds
        """
        self.rtsp_url = rtsp_url
        self.username = username
        self.password = password
        self.timeout = timeout
        self._connected = False
        self._process = None
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected
    
    def get_authenticated_url(self) -> str:
        """Get RTSP URL with authentication credentials
        
        Returns:
            RTSP URL with username and password
        """
        if not self.username or not self.password:
            return self.rtsp_url
        
        parsed = urlparse(self.rtsp_url)
        
        # Reconstruct URL with credentials
        authenticated_url = f"{parsed.scheme}://{self.username}:{self.password}@{parsed.netloc}{parsed.path}"
        
        if parsed.query:
            authenticated_url += f"?{parsed.query}"
        
        return authenticated_url
    
    def parse_rtsp_url(self) -> dict:
        """Parse RTSP URL into components
        
        Returns:
            Dictionary with URL components
        """
        parsed = urlparse(self.rtsp_url)
        
        return {
            "scheme": parsed.scheme,
            "host": parsed.hostname,
            "port": parsed.port or 554,
            "path": parsed.path,
            "query": parsed.query,
        }
    
    async def test_connection(self) -> Tuple[bool, str]:
        """Test RTSP connection
        
        Returns:
            Tuple of (success, message)
        """
        try:
            # Use FFmpeg to test connection
            import subprocess
            
            cmd = [
                "ffprobe",
                "-v", "error",
                "-timeout", str(self.timeout * 1000000),  # microseconds
                "-show_streams",
                "-select_streams", "v:0",
                self.get_authenticated_url(),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.timeout,
                )
                
                if process.returncode == 0:
                    self._connected = True
                    return True, "Connection successful"
                else:
                    error_msg = stderr.decode() if stderr else "Unknown error"
                    return False, f"Connection failed: {error_msg}"
            
            except asyncio.TimeoutError:
                process.kill()
                return False, "Connection timeout"
            
        except FileNotFoundError:
            return False, "FFprobe not found"
        except Exception as e:
            return False, f"Connection error: {str(e)}"
    
    async def get_stream_info(self) -> Optional[dict]:
        """Get stream information
        
        Returns:
            Dictionary with stream info or None if failed
        """
        try:
            import subprocess
            import json
            
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_streams",
                "-select_streams", "v:0",
                self.get_authenticated_url(),
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout,
            )
            
            if process.returncode == 0:
                data = json.loads(stdout.decode())
                if data.get("streams"):
                    stream = data["streams"][0]
                    return {
                        "codec": stream.get("codec_name"),
                        "width": stream.get("width"),
                        "height": stream.get("height"),
                        "fps": self._parse_fps(stream.get("r_frame_rate")),
                        "bitrate": stream.get("bit_rate"),
                    }
            
            return None
            
        except Exception as e:
            return None
    
    def _parse_fps(self, fps_str: Optional[str]) -> Optional[float]:
        """Parse FPS string to float
        
        Args:
            fps_str: FPS string (e.g., "30/1" or "30")
            
        Returns:
            FPS as float or None
        """
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
    
    async def disconnect(self) -> None:
        """Disconnect from RTSP stream"""
        self._connected = False
        if self._process:
            self._process.kill()
            self._process = None


async def test_rtsp_connection(
    rtsp_url: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    timeout: int = 10,
) -> Tuple[bool, str, Optional[dict]]:
    """Test RTSP connection and get stream info
    
    Args:
        rtsp_url: RTSP stream URL
        username: Optional username for authentication
        password: Optional password for authentication
        timeout: Connection timeout in seconds
        
    Returns:
        Tuple of (success, message, stream_info)
    """
    client = RTSPClient(rtsp_url, username, password, timeout)
    
    success, message = await client.test_connection()
    
    if success:
        stream_info = await client.get_stream_info()
        return True, message, stream_info
    
    await client.disconnect()
    return False, message, None


def validate_rtsp_url(rtsp_url: str) -> bool:
    """Validate RTSP URL format
    
    Args:
        rtsp_url: RTSP URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not rtsp_url:
        return False
    
    parsed = urlparse(rtsp_url)
    
    # Check scheme
    if parsed.scheme not in ("rtsp", "rtsps"):
        return False
    
    # Check host
    if not parsed.hostname:
        return False
    
    # Check path
    if not parsed.path:
        return False
    
    return True


def extract_rtsp_credentials(rtsp_url: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract username and password from RTSP URL
    
    Args:
        rtsp_url: RTSP URL
        
    Returns:
        Tuple of (username, password)
    """
    parsed = urlparse(rtsp_url)
    
    if parsed.username and parsed.password:
        return parsed.username, parsed.password
    
    return None, None
