"""
VMS Telegram Bot
Telegram bot for Video Management System notifications and control
"""

import os
import logging
from typing import Optional
from datetime import datetime

import httpx
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(storage=MemoryStorage())

# HTTP client for backend communication
http_client = httpx.AsyncClient(timeout=30.0)


class FormStates(StatesGroup):
    """Form states for user interactions"""
    waiting_for_camera_id = State()
    waiting_for_time_range = State()


# ==============================
# Backend API Functions
# ==============================

async def get_backend_data(endpoint: str, params: Optional[dict] = None) -> Optional[dict]:
    """Get data from backend API"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        response = await http_client.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error fetching data from backend: {e}")
        return None


async def post_backend_data(endpoint: str, data: dict) -> Optional[dict]:
    """Post data to backend API"""
    try:
        url = f"{BACKEND_URL}{endpoint}"
        response = await http_client.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error posting data to backend: {e}")
        return None


# ==============================
# Notification Functions
# ==============================

async def send_notification(message: str, parse_mode: str = "HTML") -> bool:
    """Send notification to configured chat"""
    if not CHAT_ID:
        logger.warning("CHAT_ID not configured, skipping notification")
        return False
    
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode=parse_mode)
        return True
    except Exception as e:
        logger.error(f"Error sending notification: {e}")
        return False


async def send_event_notification(event: dict) -> bool:
    """Send event notification"""
    event_type = event.get("event_type", "unknown")
    camera_name = event.get("camera_name", "Unknown Camera")
    timestamp = event.get("timestamp", datetime.now().isoformat())
    confidence = event.get("confidence", 0)
    
    emoji = {
        "motion": "📹",
        "person": "👤",
        "vehicle": "🚗",
        "face": "😊",
        "alarm": "🚨",
        "system": "⚙️"
    }.get(event_type, "📌")
    
    message = (
        f"{emoji} <b>VMS Event</b>\n\n"
        f"<b>Type:</b> {event_type.title()}\n"
        f"<b>Camera:</b> {camera_name}\n"
        f"<b>Time:</b> {timestamp}\n"
        f"<b>Confidence:</b> {confidence:.1%}\n"
    )
    
    return await send_notification(message)


async def send_camera_status_notification(camera: dict, status: str) -> bool:
    """Send camera status change notification"""
    camera_name = camera.get("name", "Unknown Camera")
    emoji = "🟢" if status == "online" else "🔴"
    
    message = (
        f"{emoji} <b>Camera Status Change</b>\n\n"
        f"<b>Camera:</b> {camera_name}\n"
        f"<b>Status:</b> {status.upper()}\n"
        f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    
    return await send_notification(message)


async def send_recording_notification(recording: dict) -> bool:
    """Send recording notification"""
    camera_name = recording.get("camera_name", "Unknown Camera")
    duration = recording.get("duration", 0)
    file_size = recording.get("file_size", 0)
    
    message = (
        f"🎥 <b>New Recording</b>\n\n"
        f"<b>Camera:</b> {camera_name}\n"
        f"<b>Duration:</b> {duration}s\n"
        f"<b>Size:</b> {file_size / (1024 * 1024):.2f} MB\n"
        f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    
    return await send_notification(message)


async def send_system_alert(alert: dict) -> bool:
    """Send system alert notification"""
    alert_type = alert.get("type", "info")
    message = alert.get("message", "System alert")
    
    emoji = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "critical": "🚨"
    }.get(alert_type, "📌")
    
    text = (
        f"{emoji} <b>System Alert</b>\n\n"
        f"<b>Type:</b> {alert_type.upper()}\n"
        f"<b>Message:</b> {message}\n"
        f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    
    return await send_notification(text)


# ==============================
# Command Handlers
# ==============================

@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📹 Cameras", callback_data="cameras"),
            InlineKeyboardButton(text="📊 Status", callback_data="status")
        ],
        [
            InlineKeyboardButton(text="🎬 Recordings", callback_data="recordings"),
            InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")
        ]
    ])
    
    await message.answer(
        "<b>VMS Telegram Bot</b>\n\n"
        "Welcome to the Video Management System bot!\n"
        "Use the buttons below to navigate:",
        reply_markup=keyboard
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command"""
    help_text = (
        "<b>VMS Telegram Bot Commands:</b>\n\n"
        "/start - Show main menu\n"
        "/help - Show this help message\n"
        "/status - Get system status\n"
        "/cameras - List all cameras\n"
        "/events - Get recent events\n"
        "/recordings - Get recent recordings\n"
        "/start_camera <id> - Start camera\n"
        "/stop_camera <id> - Stop camera\n"
        "/snapshot <id> - Get camera snapshot\n"
    )
    await message.answer(help_text)


@dp.message(Command("status"))
async def cmd_status(message: Message) -> None:
    """Handle /status command"""
    data = await get_backend_data("/health")
    
    if data:
        status_text = (
            "<b>📊 System Status</b>\n\n"
            f"<b>Status:</b> ✅ Online\n"
            f"<b>Backend:</b> {BACKEND_URL}\n"
            f"<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
    else:
        status_text = (
            "<b>📊 System Status</b>\n\n"
            "<b>Status:</b> ❌ Offline\n"
            "<b>Backend:</b> Connection failed\n"
        )
    
    await message.answer(status_text)


@dp.message(Command("cameras"))
async def cmd_cameras(message: Message) -> None:
    """Handle /cameras command"""
    data = await get_backend_data("/api/cameras")
    
    if not data:
        await message.answer("❌ Failed to fetch cameras")
        return
    
    if isinstance(data, dict) and "items" in data:
        cameras = data["items"]
    elif isinstance(data, list):
        cameras = data
    else:
        cameras = []
    
    if not cameras:
        await message.answer("📹 No cameras found")
        return
    
    text = "<b>📹 Cameras List</b>\n\n"
    for camera in cameras[:10]:  # Limit to first 10 cameras
        status = "🟢" if camera.get("is_active") else "🔴"
        text += (
            f"{status} <b>{camera.get('name', 'Unknown')}</b>\n"
            f"   ID: {camera.get('id')}\n"
            f"   Status: {'Active' if camera.get('is_active') else 'Inactive'}\n\n"
        )
    
    if len(cameras) > 10:
        text += f"... and {len(cameras) - 10} more cameras"
    
    await message.answer(text)


@dp.message(Command("events"))
async def cmd_events(message: Message) -> None:
    """Handle /events command"""
    data = await get_backend_data("/api/events", params={"limit": 10})
    
    if not data:
        await message.answer("❌ Failed to fetch events")
        return
    
    if isinstance(data, dict) and "items" in data:
        events = data["items"]
    elif isinstance(data, list):
        events = data
    else:
        events = []
    
    if not events:
        await message.answer("📌 No events found")
        return
    
    text = "<b>📌 Recent Events</b>\n\n"
    for event in events:
        emoji = {
            "motion": "📹",
            "person": "👤",
            "vehicle": "🚗",
            "face": "😊",
            "alarm": "🚨"
        }.get(event.get("event_type"), "📌")
        
        text += (
            f"{emoji} <b>{event.get('event_type', 'unknown').title()}</b>\n"
            f"   Camera: {event.get('camera_name', 'Unknown')}\n"
            f"   Time: {event.get('timestamp', 'N/A')}\n\n"
        )
    
    await message.answer(text)


@dp.message(Command("recordings"))
async def cmd_recordings(message: Message) -> None:
    """Handle /recordings command"""
    data = await get_backend_data("/api/recordings", params={"limit": 10})
    
    if not data:
        await message.answer("❌ Failed to fetch recordings")
        return
    
    if isinstance(data, dict) and "items" in data:
        recordings = data["items"]
    elif isinstance(data, list):
        recordings = data
    else:
        recordings = []
    
    if not recordings:
        await message.answer("🎬 No recordings found")
        return
    
    text = "<b>🎬 Recent Recordings</b>\n\n"
    for recording in recordings:
        duration = recording.get("duration", 0)
        size_mb = recording.get("file_size", 0) / (1024 * 1024)
        
        text += (
            f"🎥 <b>Recording</b>\n"
            f"   Camera: {recording.get('camera_name', 'Unknown')}\n"
            f"   Duration: {duration}s\n"
            f"   Size: {size_mb:.2f} MB\n"
            f"   Time: {recording.get('start_time', 'N/A')}\n\n"
        )
    
    await message.answer(text)


@dp.message(Command("start_camera"))
async def cmd_start_camera(message: Message) -> None:
    """Handle /start_camera command"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /start_camera <camera_id>")
        return
    
    camera_id = args[1]
    data = await post_backend_data(f"/api/cameras/{camera_id}/start", {})
    
    if data:
        await message.answer(f"✅ Camera {camera_id} started successfully")
    else:
        await message.answer(f"❌ Failed to start camera {camera_id}")


@dp.message(Command("stop_camera"))
async def cmd_stop_camera(message: Message) -> None:
    """Handle /stop_camera command"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /stop_camera <camera_id>")
        return
    
    camera_id = args[1]
    data = await post_backend_data(f"/api/cameras/{camera_id}/stop", {})
    
    if data:
        await message.answer(f"✅ Camera {camera_id} stopped successfully")
    else:
        await message.answer(f"❌ Failed to stop camera {camera_id}")


@dp.message(Command("snapshot"))
async def cmd_snapshot(message: Message) -> None:
    """Handle /snapshot command"""
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /snapshot <camera_id>")
        return
    
    camera_id = args[1]
    data = await get_backend_data(f"/api/cameras/{camera_id}/snapshot")
    
    if data and "image" in data:
        await message.answer_photo(
            photo=data["image"],
            caption=f"📸 Snapshot from camera {camera_id}"
        )
    else:
        await message.answer(f"❌ Failed to get snapshot from camera {camera_id}")


# ==============================
# Callback Query Handlers
# ==============================

@dp.callback_query(lambda c: c.data == "cameras")
async def callback_cameras(callback: CallbackQuery) -> None:
    """Handle cameras button callback"""
    await cmd_cameras(callback.message)
    await callback.answer()


@dp.callback_query(lambda c: c.data == "status")
async def callback_status(callback: CallbackQuery) -> None:
    """Handle status button callback"""
    await cmd_status(callback.message)
    await callback.answer()


@dp.callback_query(lambda c: c.data == "recordings")
async def callback_recordings(callback: CallbackQuery) -> None:
    """Handle recordings button callback"""
    await cmd_recordings(callback.message)
    await callback.answer()


@dp.callback_query(lambda c: c.data == "settings")
async def callback_settings(callback: CallbackQuery) -> None:
    """Handle settings button callback"""
    text = (
        "<b>⚙️ Bot Settings</b>\n\n"
        f"<b>Backend URL:</b> {BACKEND_URL}\n"
        f"<b>Chat ID:</b> {CHAT_ID or 'Not configured'}\n"
        f"<b>Webhook:</b> {'Enabled' if WEBHOOK_URL else 'Disabled'}\n"
    )
    await callback.message.answer(text)
    await callback.answer()


# ==============================
# Main Entry Point
# ==============================

async def main() -> None:
    """Main function to start the bot"""
    logger.info("Starting VMS Telegram Bot...")
    
    # Set webhook if configured
    if WEBHOOK_URL:
        try:
            await bot.set_webhook(
                url=WEBHOOK_URL,
                secret_token=WEBHOOK_SECRET
            )
            logger.info(f"Webhook set to: {WEBHOOK_URL}")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")
    
    # Start polling (if webhook not configured)
    if not WEBHOOK_URL:
        await dp.start_polling(bot)
    else:
        # For webhook mode, just keep the bot running
        logger.info("Bot running in webhook mode")
        # Keep the bot alive
        while True:
            await asyncio.sleep(3600)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
