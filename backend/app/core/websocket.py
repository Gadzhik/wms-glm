"""WebSocket connection manager for real-time communication"""
import json
import asyncio
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

from app.config import settings


class ConnectionManager:
    """Manager for WebSocket connections"""
    
    def __init__(self):
        """Initialize connection manager"""
        # Active connections: {user_id: {connection_id: WebSocket}}
        self.active_connections: Dict[int, Dict[str, WebSocket]] = {}
        # Camera subscriptions: {camera_id: set of user_ids}
        self.camera_subscriptions: Dict[int, Set[int]] = {}
        # Connection metadata: {connection_id: {user_id, camera_id, connected_at}}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        # Connection counter for generating unique IDs
        self._connection_counter = 0
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, user_id: int) -> str:
        """Accept a new WebSocket connection
        
        Args:
            websocket: WebSocket connection
            user_id: User ID
            
        Returns:
            Connection ID
        """
        await websocket.accept()
        
        async with self._lock:
            # Generate unique connection ID
            self._connection_counter += 1
            connection_id = f"{user_id}_{self._connection_counter}"
            
            # Store connection
            if user_id not in self.active_connections:
                self.active_connections[user_id] = {}
            
            self.active_connections[user_id][connection_id] = websocket
            
            # Store metadata
            self.connection_metadata[connection_id] = {
                "user_id": user_id,
                "camera_id": None,
                "connected_at": datetime.utcnow().isoformat(),
            }
            
            # Check connection limit
            total_connections = sum(
                len(conns) for conns in self.active_connections.values()
            )
            if total_connections > settings.WS_MAX_CONNECTIONS:
                await self.disconnect(connection_id, reason="Max connections reached")
                return connection_id
            
            return connection_id
    
    async def disconnect(self, connection_id: str, reason: str = "Disconnected") -> None:
        """Disconnect a WebSocket connection
        
        Args:
            connection_id: Connection ID to disconnect
            reason: Disconnect reason
        """
        async with self._lock:
            # Get metadata
            metadata = self.connection_metadata.get(connection_id)
            if not metadata:
                return
            
            user_id = metadata["user_id"]
            camera_id = metadata["camera_id"]
            
            # Remove connection
            if user_id in self.active_connections:
                if connection_id in self.active_connections[user_id]:
                    websocket = self.active_connections[user_id][connection_id]
                    try:
                        await websocket.close(code=1000, reason=reason)
                    except Exception:
                        pass
                    del self.active_connections[user_id][connection_id]
                
                # Clean up empty user dict
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]
            
            # Remove from camera subscriptions
            if camera_id and camera_id in self.camera_subscriptions:
                self.camera_subscriptions[camera_id].discard(user_id)
                if not self.camera_subscriptions[camera_id]:
                    del self.camera_subscriptions[camera_id]
            
            # Remove metadata
            del self.connection_metadata[connection_id]
    
    async def subscribe_camera(self, connection_id: str, camera_id: int) -> bool:
        """Subscribe a connection to a camera stream
        
        Args:
            connection_id: Connection ID
            camera_id: Camera ID to subscribe
            
        Returns:
            True if subscribed successfully
        """
        async with self._lock:
            # Get metadata
            metadata = self.connection_metadata.get(connection_id)
            if not metadata:
                return False
            
            user_id = metadata["user_id"]
            
            # Update metadata
            metadata["camera_id"] = camera_id
            
            # Add to camera subscriptions
            if camera_id not in self.camera_subscriptions:
                self.camera_subscriptions[camera_id] = set()
            self.camera_subscriptions[camera_id].add(user_id)
            
            return True
    
    async def unsubscribe_camera(self, connection_id: str) -> None:
        """Unsubscribe a connection from camera stream
        
        Args:
            connection_id: Connection ID
        """
        async with self._lock:
            # Get metadata
            metadata = self.connection_metadata.get(connection_id)
            if not metadata:
                return
            
            user_id = metadata["user_id"]
            camera_id = metadata["camera_id"]
            
            # Remove from camera subscriptions
            if camera_id and camera_id in self.camera_subscriptions:
                self.camera_subscriptions[camera_id].discard(user_id)
                if not self.camera_subscriptions[camera_id]:
                    del self.camera_subscriptions[camera_id]
            
            # Update metadata
            metadata["camera_id"] = None
    
    async def send_personal_message(self, message: dict, user_id: int) -> int:
        """Send a message to a specific user
        
        Args:
            message: Message to send (will be JSON encoded)
            user_id: User ID to send to
            
        Returns:
            Number of connections message was sent to
        """
        if user_id not in self.active_connections:
            return 0
        
        message_json = json.dumps(message)
        sent_count = 0
        
        for connection_id, websocket in self.active_connections[user_id].items():
            try:
                await websocket.send_text(message_json)
                sent_count += 1
            except Exception:
                # Connection might be dead, schedule cleanup
                asyncio.create_task(self.disconnect(connection_id, "Send failed"))
        
        return sent_count
    
    async def broadcast_to_camera(self, message: dict, camera_id: int) -> int:
        """Broadcast a message to all subscribers of a camera
        
        Args:
            message: Message to send (will be JSON encoded)
            camera_id: Camera ID
            
        Returns:
            Number of connections message was sent to
        """
        if camera_id not in self.camera_subscriptions:
            return 0
        
        message_json = json.dumps(message)
        sent_count = 0
        
        for user_id in self.camera_subscriptions[camera_id]:
            if user_id in self.active_connections:
                for connection_id, websocket in self.active_connections[user_id].items():
                    metadata = self.connection_metadata.get(connection_id)
                    if metadata and metadata.get("camera_id") == camera_id:
                        try:
                            await websocket.send_text(message_json)
                            sent_count += 1
                        except Exception:
                            asyncio.create_task(self.disconnect(connection_id, "Send failed"))
        
        return sent_count
    
    async def broadcast(self, message: dict) -> int:
        """Broadcast a message to all connected clients
        
        Args:
            message: Message to send (will be JSON encoded)
            
        Returns:
            Number of connections message was sent to
        """
        message_json = json.dumps(message)
        sent_count = 0
        
        for user_id, connections in self.active_connections.items():
            for connection_id, websocket in connections.items():
                try:
                    await websocket.send_text(message_json)
                    sent_count += 1
                except Exception:
                    asyncio.create_task(self.disconnect(connection_id, "Send failed"))
        
        return sent_count
    
    async def send_binary_to_camera(self, data: bytes, camera_id: int) -> int:
        """Send binary data to camera subscribers (for video frames)
        
        Args:
            data: Binary data to send
            camera_id: Camera ID
            
        Returns:
            Number of connections data was sent to
        """
        if camera_id not in self.camera_subscriptions:
            return 0
        
        sent_count = 0
        
        for user_id in self.camera_subscriptions[camera_id]:
            if user_id in self.active_connections:
                for connection_id, websocket in self.active_connections[user_id].items():
                    metadata = self.connection_metadata.get(connection_id)
                    if metadata and metadata.get("camera_id") == camera_id:
                        try:
                            await websocket.send_bytes(data)
                            sent_count += 1
                        except Exception:
                            asyncio.create_task(self.disconnect(connection_id, "Send failed"))
        
        return sent_count
    
    def get_connection_count(self) -> int:
        """Get total number of active connections
        
        Returns:
            Number of active connections
        """
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of connections for a specific user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of connections for the user
        """
        return len(self.active_connections.get(user_id, {}))
    
    def get_camera_subscriber_count(self, camera_id: int) -> int:
        """Get number of subscribers for a camera
        
        Args:
            camera_id: Camera ID
            
        Returns:
            Number of subscribers
        """
        return len(self.camera_subscriptions.get(camera_id, set()))
    
    def get_connected_users(self) -> Set[int]:
        """Get set of connected user IDs
        
        Returns:
            Set of user IDs
        """
        return set(self.active_connections.keys())


# Global connection manager instance
manager = ConnectionManager()


# Convenience functions
async def broadcast_message(message: dict) -> int:
    """Broadcast a message to all connected clients
    
    Args:
        message: Message to send
        
    Returns:
        Number of connections message was sent to
    """
    return await manager.broadcast(message)


async def send_personal_message(message: dict, user_id: int) -> int:
    """Send a message to a specific user
    
    Args:
        message: Message to send
        user_id: User ID
        
    Returns:
        Number of connections message was sent to
    """
    return await manager.send_personal_message(message, user_id)
