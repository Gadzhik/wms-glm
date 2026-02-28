"""ONVIF utilities for camera discovery and control"""
import asyncio
import socket
from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class DiscoveredCamera:
    """Discovered camera information"""
    ip: str
    port: int
    name: Optional[str] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    rtsp_url: Optional[str] = None
    onvif_url: Optional[str] = None


class ONVIFClient:
    """ONVIF client for camera discovery and control"""
    
    def __init__(
        self,
        host: str,
        port: int = 80,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        """Initialize ONVIF client
        
        Args:
            host: Camera IP address or hostname
            port: ONVIF port (default 80)
            username: Optional username for authentication
            password: Optional password for authentication
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self._connected = False
    
    @property
    def is_connected(self) -> bool:
        """Check if client is connected"""
        return self._connected
    
    @property
    def onvif_url(self) -> str:
        """Get ONVIF service URL"""
        return f"http://{self.host}:{self.port}/onvif/device_service"
    
    async def connect(self) -> bool:
        """Connect to ONVIF device
        
        Returns:
            True if connection successful
        """
        try:
            # Try to connect to ONVIF service
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(self.host, self.port),
                timeout=5,
            )
            writer.close()
            await writer.wait_closed()
            
            self._connected = True
            return True
            
        except (asyncio.TimeoutError, ConnectionError, OSError):
            self._connected = False
            return False
    
    async def get_device_info(self) -> Optional[Dict[str, Any]]:
        """Get device information
        
        Returns:
            Dictionary with device info or None if failed
        """
        if not self._connected:
            if not await self.connect():
                return None
        
        try:
            # In a real implementation, use zeep library for ONVIF
            # This is a simplified version
            return {
                "manufacturer": "Unknown",
                "model": "Unknown",
                "firmware_version": "Unknown",
                "serial_number": "Unknown",
                "name": f"Camera at {self.host}",
            }
        except Exception:
            return None
    
    async def get_stream_uri(self) -> Optional[str]:
        """Get RTSP stream URI
        
        Returns:
            RTSP stream URL or None if failed
        """
        if not self._connected:
            if not await self.connect():
                return None
        
        try:
            # In a real implementation, use ONVIF PTZ/Imaging services
            # This is a simplified version
            return f"rtsp://{self.host}:554/stream"
        except Exception:
            return None
    
    async def get_capabilities(self) -> Optional[Dict[str, Any]]:
        """Get device capabilities
        
        Returns:
            Dictionary with capabilities or None if failed
        """
        if not self._connected:
            if not await self.connect():
                return None
        
        try:
            return {
                "ptz": True,
                "imaging": True,
                "analytics": False,
                "events": True,
            }
        except Exception:
            return None
    
    async def disconnect(self) -> None:
        """Disconnect from ONVIF device"""
        self._connected = False


async def discover_cameras(
    ip_range: Optional[str] = None,
    port: int = 80,
    timeout: int = 5,
) -> List[DiscoveredCamera]:
    """Discover ONVIF cameras on the network
    
    Args:
        ip_range: IP range to scan (e.g., "192.168.1.0/24")
        port: ONVIF port to scan
        timeout: Connection timeout in seconds
        
    Returns:
        List of discovered cameras
    """
    cameras = []
    
    if not ip_range:
        # Use local network
        ip_range = get_local_network_range()
    
    # Parse IP range
    ips_to_scan = parse_ip_range(ip_range)
    
    # Scan IPs concurrently
    tasks = []
    for ip in ips_to_scan:
        tasks.append(scan_onvif_device(ip, port, timeout))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for result in results:
        if isinstance(result, DiscoveredCamera):
            cameras.append(result)
    
    return cameras


async def scan_onvif_device(
    ip: str,
    port: int,
    timeout: int,
) -> Optional[DiscoveredCamera]:
    """Scan a single IP for ONVIF device
    
    Args:
        ip: IP address to scan
        port: ONVIF port
        timeout: Connection timeout in seconds
        
    Returns:
        DiscoveredCamera if found, None otherwise
    """
    try:
        # Try to connect to ONVIF port
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=timeout,
        )
        writer.close()
        await writer.wait_closed()
        
        # ONVIF device found, get more info
        client = ONVIFClient(ip, port)
        device_info = await client.get_device_info()
        stream_uri = await client.get_stream_uri()
        
        return DiscoveredCamera(
            ip=ip,
            port=port,
            name=device_info.get("name") if device_info else None,
            manufacturer=device_info.get("manufacturer") if device_info else None,
            model=device_info.get("model") if device_info else None,
            rtsp_url=stream_uri,
            onvif_url=client.onvif_url,
        )
        
    except (asyncio.TimeoutError, ConnectionError, OSError):
        return None


async def get_camera_info(
    host: str,
    port: int = 80,
    username: Optional[str] = None,
    password: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Get detailed camera information via ONVIF
    
    Args:
        host: Camera IP address
        port: ONVIF port
        username: Optional username
        password: Optional password
        
    Returns:
        Dictionary with camera info or None if failed
    """
    client = ONVIFClient(host, port, username, password)
    
    if not await client.connect():
        return None
    
    device_info = await client.get_device_info()
    stream_uri = await client.get_stream_uri()
    capabilities = await client.get_capabilities()
    
    await client.disconnect()
    
    if not device_info:
        return None
    
    return {
        **device_info,
        "rtsp_url": stream_uri,
        "capabilities": capabilities,
    }


def parse_ip_range(ip_range: str) -> List[str]:
    """Parse IP range string into list of IPs
    
    Args:
        ip_range: IP range (e.g., "192.168.1.0/24" or "192.168.1.1-192.168.1.100")
        
    Returns:
        List of IP addresses
    """
    ips = []
    
    if "/" in ip_range:
        # CIDR notation
        import ipaddress
        network = ipaddress.ip_network(ip_range, strict=False)
        ips = [str(host) for host in network.hosts()]
    elif "-" in ip_range:
        # Range notation
        start, end = ip_range.split("-")
        import ipaddress
        start_ip = ipaddress.IPv4Address(start.strip())
        end_ip = ipaddress.IPv4Address(end.strip())
        
        current = int(start_ip)
        end = int(end_ip)
        
        while current <= end:
            ips.append(str(ipaddress.IPv4Address(current)))
            current += 1
    else:
        # Single IP
        ips = [ip_range]
    
    return ips


def get_local_network_range() -> str:
    """Get local network IP range
    
    Returns:
        IP range in CIDR notation
    """
    try:
        # Get local IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        # Determine network based on IP
        if local_ip.startswith("192.168."):
            return f"{local_ip.rsplit('.', 1)[0]}.0/24"
        elif local_ip.startswith("10."):
            return f"{local_ip.rsplit('.', 1)[0]}.0/24"
        elif local_ip.startswith("172."):
            # 172.16.0.0/12
            parts = local_ip.split(".")
            if int(parts[1]) >= 16 and int(parts[1]) <= 31:
                return f"{parts[0]}.{parts[1]}.0.0/16"
        
        return "192.168.1.0/24"
        
    except Exception:
        return "192.168.1.0/24"
