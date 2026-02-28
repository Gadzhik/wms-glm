"""Cleanup worker for old files and storage management"""
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recording import Recording
from app.models.event import Event
from app.services.storage_service import storage_service
from app.services.notification_service import notification_service
from app.config import settings


class CleanupWorker:
    """Background worker for cleanup and storage management"""
    
    def __init__(self, db: AsyncSession):
        """Initialize cleanup worker
        
        Args:
            db: Database session
        """
        self.db = db
        self._running = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """Start cleanup worker"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._run_cleanup())
    
    async def stop(self) -> None:
        """Stop cleanup worker"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
    
    async def _run_cleanup(self) -> None:
        """Run cleanup tasks periodically"""
        while self._running:
            try:
                await self._cleanup_old_files()
                await self._check_storage_space()
                await self._cleanup_old_events()
                await asyncio.sleep(settings.CLEANUP_INTERVAL_HOURS * 3600)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Cleanup worker error: {e}")
                await asyncio.sleep(3600)  # Wait before retry
    
    async def _cleanup_old_files(self) -> None:
        """Cleanup old files based on retention policy"""
        result = await storage_service.cleanup_old_files(
            retention_days=settings.RETENTION_DAYS,
            dry_run=False,
        )
        
        print(f"Cleanup result: {result}")
    
    async def _check_storage_space(self) -> None:
        """Check storage space and alert if needed"""
        usage = storage_service.get_disk_usage()
        
        # Check if storage is full
        if usage["usage_percent"] >= 95:
            # Create storage full event
            event = Event(
                event_type=Event.EVENT_TYPE_STORAGE_FULL,
                details={
                    "usage_percent": usage["usage_percent"],
                    "free_gb": usage["free_gb"],
                },
                timestamp=datetime.utcnow().isoformat(),
                status="new",
            )
            
            self.db.add(event)
            await self.db.commit()
            
            # Send notification
            await notification_service.send_storage_full_notification(
                usage["usage_percent"],
                usage["free_gb"],
            )
    
    async def _cleanup_old_events(self) -> None:
        """Cleanup old events from database"""
        cutoff_date = datetime.utcnow() - timedelta(days=7)
        
        # Delete old events except resolved
        result = await self.db.execute(
            select(Event).where(
                (Event.timestamp < cutoff_date) &
                (Event.status != "resolved")
            )
        )
        old_events = list(result.scalars().all())
        
        for event in old_events:
            await self.db.delete(event)
        
        await self.db.commit()
        
        print(f"Cleaned up {len(old_events)} old events")
    
    async def get_cleanup_stats(self) -> dict:
        """Get cleanup statistics
        
        Returns:
            Cleanup statistics
        """
        # Get recordings count
        result = await self.db.execute(select(func.count(Recording.id)))
        total_recordings = result.scalar() or 0
        
        # Get disk usage
        usage = storage_service.get_disk_usage()
        
        return {
            "total_recordings": total_recordings,
            "disk_usage_gb": usage["used_gb"],
            "disk_free_gb": usage["free_gb"],
            "disk_usage_percent": usage["usage_percent"],
            "retention_days": settings.RETENTION_DAYS,
        }
    
    async def run_manual_cleanup(self, retention_days: Optional[int] = None) -> dict:
        """Run manual cleanup
        
        Args:
            retention_days: Custom retention days
            
        Returns:
            Cleanup results
        """
        return await storage_service.cleanup_old_files(retention_days, dry_run=False)
