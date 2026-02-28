"""Notification service for sending alerts"""
import asyncio
import httpx
from typing import Optional, Dict, Any
from datetime import datetime

from app.config import settings


class NotificationService:
    """Notification service"""
    
    def __init__(self):
        """Initialize notification service"""
        self.telegram_enabled = settings.TELEGRAM_ENABLED
        self.telegram_bot_token = settings.TELEGRAM_BOT_TOKEN
        self.telegram_chat_id = settings.TELEGRAM_CHAT_ID
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client
        
        Returns:
            HTTP client
        """
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client"""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
    
    async def send_telegram_notification(
        self,
        message: str,
        parse_mode: str = "HTML",
    ) -> bool:
        """Send notification via Telegram
        
        Args:
            message: Message to send
            parse_mode: Parse mode (HTML or Markdown)
            
        Returns:
            True if sent successfully
        """
        if not self.telegram_enabled:
            return False
        
        if not self.telegram_bot_token or not self.telegram_chat_id:
            return False
        
        try:
            client = await self._get_http_client()
            
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            
            payload = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": parse_mode,
            }
            
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            return response.json().get("ok", False)
            
        except Exception as e:
            print(f"Failed to send Telegram notification: {e}")
            return False
    
    async def send_person_detected_notification(
        self,
        camera_name: str,
        confidence: float,
        timestamp: str,
    ) -> bool:
        """Send person detected notification
        
        Args:
            camera_name: Camera name
            confidence: Detection confidence
            timestamp: Detection timestamp
            
        Returns:
            True if sent successfully
        """
        message = (
            f"🚨 <b>Person Detected</b>\n\n"
            f"📹 Camera: {camera_name}\n"
            f"🎯 Confidence: {confidence:.1%}\n"
            f"⏰ Time: {timestamp}"
        )
        
        return await self.send_telegram_notification(message)
    
    async def send_motion_detected_notification(
        self,
        camera_name: str,
        level: float,
        timestamp: str,
    ) -> bool:
        """Send motion detected notification
        
        Args:
            camera_name: Camera name
            level: Motion level
            timestamp: Detection timestamp
            
        Returns:
            True if sent successfully
        """
        message = (
            f"👋 <b>Motion Detected</b>\n\n"
            f"📹 Camera: {camera_name}\n"
            f"📊 Level: {level:.1%}\n"
            f"⏰ Time: {timestamp}"
        )
        
        return await self.send_telegram_notification(message)
    
    async def send_camera_offline_notification(
        self,
        camera_name: str,
        offline_since: str,
    ) -> bool:
        """Send camera offline notification
        
        Args:
            camera_name: Camera name
            offline_since: Time when camera went offline
            
        Returns:
            True if sent successfully
        """
        message = (
            f"🔴 <b>Camera Offline</b>\n\n"
            f"📹 Camera: {camera_name}\n"
            f"⏰ Since: {offline_since}"
        )
        
        return await self.send_telegram_notification(message)
    
    async def send_camera_error_notification(
        self,
        camera_name: str,
        error_message: str,
    ) -> bool:
        """Send camera error notification
        
        Args:
            camera_name: Camera name
            error_message: Error message
            
        Returns:
            True if sent successfully
        """
        message = (
            f"⚠️ <b>Camera Error</b>\n\n"
            f"📹 Camera: {camera_name}\n"
            f"❌ Error: {error_message}"
        )
        
        return await self.send_telegram_notification(message)
    
    async def send_storage_full_notification(
        self,
        usage_percent: float,
        free_gb: float,
    ) -> bool:
        """Send storage full notification
        
        Args:
            usage_percent: Storage usage percentage
            free_gb: Free space in GB
            
        Returns:
            True if sent successfully
        """
        message = (
            f"💾 <b>Storage Full Warning</b>\n\n"
            f"📊 Usage: {usage_percent:.1f}%\n"
            f"💿 Free: {free_gb:.1f} GB"
        )
        
        return await self.send_telegram_notification(message)
    
    async def send_system_error_notification(
        self,
        error_message: str,
        component: str,
    ) -> bool:
        """Send system error notification
        
        Args:
            error_message: Error message
            component: Component that failed
            
        Returns:
            True if sent successfully
        """
        message = (
            f"🔧 <b>System Error</b>\n\n"
            f"🔌 Component: {component}\n"
            f"❌ Error: {error_message}"
        )
        
        return await self.send_telegram_notification(message)
    
    async def send_notification(
        self,
        event_type: str,
        data: Dict[str, Any],
    ) -> bool:
        """Send notification based on event type
        
        Args:
            event_type: Type of event
            data: Event data
            
        Returns:
            True if sent successfully
        """
        if event_type == "person_detected":
            return await self.send_person_detected_notification(
                camera_name=data.get("camera_name", "Unknown"),
                confidence=data.get("confidence", 0.0),
                timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            )
        elif event_type == "motion_detected":
            return await self.send_motion_detected_notification(
                camera_name=data.get("camera_name", "Unknown"),
                level=data.get("level", 0.0),
                timestamp=data.get("timestamp", datetime.utcnow().isoformat()),
            )
        elif event_type == "camera_offline":
            return await self.send_camera_offline_notification(
                camera_name=data.get("camera_name", "Unknown"),
                offline_since=data.get("offline_since", datetime.utcnow().isoformat()),
            )
        elif event_type == "camera_error":
            return await self.send_camera_error_notification(
                camera_name=data.get("camera_name", "Unknown"),
                error_message=data.get("error_message", "Unknown error"),
            )
        elif event_type == "storage_full":
            return await self.send_storage_full_notification(
                usage_percent=data.get("usage_percent", 0.0),
                free_gb=data.get("free_gb", 0.0),
            )
        elif event_type == "system_error":
            return await self.send_system_error_notification(
                error_message=data.get("error_message", "Unknown error"),
                component=data.get("component", "Unknown"),
            )
        
        return False


# Global notification service instance
notification_service = NotificationService()


# Convenience functions
async def send_notification(
    event_type: str,
    data: Dict[str, Any],
) -> bool:
    """Send notification"""
    return await notification_service.send_notification(event_type, data)


async def send_telegram_notification(
    message: str,
    parse_mode: str = "HTML",
) -> bool:
    """Send Telegram notification"""
    return await notification_service.send_telegram_notification(message, parse_mode)
