"""Schedule service for managing recording schedules"""
from typing import Optional, List
from datetime import datetime, time

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.camera import Camera
from app.models.schedule import Schedule


class ScheduleService:
    """Schedule management service"""
    
    def __init__(self, db: AsyncSession):
        """Initialize schedule service
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_schedule(
        self,
        camera_id: int,
        days_of_week: List[int],
        start_time: str,
        end_time: str,
        record_type: str = "continuous",
        is_active: bool = True,
    ) -> Schedule:
        """Create a new schedule
        
        Args:
            camera_id: Camera ID
            days_of_week: Days of week (0-6, 0=Sunday)
            start_time: Start time (HH:MM)
            end_time: End time (HH:MM)
            record_type: Recording type (continuous or motion)
            is_active: Is schedule active
            
        Returns:
            Created schedule
        """
        import json
        
        schedule = Schedule(
            camera_id=camera_id,
            days_of_week=json.dumps(days_of_week),
            start_time=start_time,
            end_time=end_time,
            record_type=record_type,
            is_active=1 if is_active else 0,
        )
        
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return schedule
    
    async def get_schedule(self, schedule_id: int) -> Optional[Schedule]:
        """Get schedule by ID
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Schedule or None
        """
        result = await self.db.execute(
            select(Schedule).where(Schedule.id == schedule_id)
        )
        return result.scalar_one_or_none()
    
    async def get_schedules(
        self,
        camera_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Schedule]:
        """Get schedules with filtering
        
        Args:
            camera_id: Filter by camera
            is_active: Filter by active status
            skip: Number of records to skip
            limit: Maximum number of records
            
        Returns:
            List of schedules
        """
        query = select(Schedule)
        
        if camera_id is not None:
            query = query.where(Schedule.camera_id == camera_id)
        
        if is_active is not None:
            query = query.where(Schedule.is_active == (1 if is_active else 0))
        
        query = query.order_by(Schedule.id)
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_camera_schedules(self, camera_id: int) -> List[Schedule]:
        """Get all schedules for a camera
        
        Args:
            camera_id: Camera ID
            
        Returns:
            List of schedules
        """
        return await self.get_schedules(camera_id=camera_id)
    
    async def get_active_schedules(self) -> List[Schedule]:
        """Get all active schedules
        
        Returns:
            List of active schedules
        """
        return await self.get_schedules(is_active=True)
    
    async def update_schedule(
        self,
        schedule_id: int,
        days_of_week: Optional[List[int]] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        record_type: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[Schedule]:
        """Update schedule
        
        Args:
            schedule_id: Schedule ID
            days_of_week: Days of week
            start_time: Start time
            end_time: End time
            record_type: Recording type
            is_active: Is schedule active
            
        Returns:
            Updated schedule or None
        """
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return None
        
        import json
        
        if days_of_week is not None:
            schedule.days_of_week = json.dumps(days_of_week)
        if start_time is not None:
            schedule.start_time = start_time
        if end_time is not None:
            schedule.end_time = end_time
        if record_type is not None:
            schedule.record_type = record_type
        if is_active is not None:
            schedule.is_active = 1 if is_active else 0
        
        await self.db.commit()
        await self.db.refresh(schedule)
        
        return schedule
    
    async def delete_schedule(self, schedule_id: int) -> bool:
        """Delete schedule
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            True if deleted
        """
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False
        
        await self.db.delete(schedule)
        await self.db.commit()
        
        return True
    
    async def check_schedule(
        self,
        camera_id: int,
        check_time: Optional[datetime] = None,
    ) -> Optional[dict]:
        """Check if camera should be recording based on schedule
        
        Args:
            camera_id: Camera ID
            check_time: Time to check (default: now)
            
        Returns:
            Schedule info or None if no active schedule
        """
        if check_time is None:
            check_time = datetime.utcnow()
        
        schedules = await self.get_camera_schedules(camera_id)
        
        # Get current day of week (0=Sunday, 6=Saturday)
        current_day = check_time.weekday()
        current_time_minutes = check_time.hour * 60 + check_time.minute
        
        for schedule in schedules:
            if not schedule.is_active_schedule():
                continue
            
            days = schedule.get_days_of_week()
            
            # Check if current day is in schedule
            if current_day not in days:
                continue
            
            # Check if current time is in schedule range
            start_minutes = schedule.get_start_time_minutes()
            end_minutes = schedule.get_end_time_minutes()
            
            if start_minutes <= current_time_minutes < end_minutes:
                return {
                    "schedule_id": schedule.id,
                    "record_type": schedule.record_type,
                    "start_time": schedule.start_time,
                    "end_time": schedule.end_time,
                }
        
        return None
    
    async def get_schedules_for_time(
        self,
        check_time: Optional[datetime] = None,
    ) -> List[Schedule]:
        """Get all schedules that should be active at given time
        
        Args:
            check_time: Time to check (default: now)
            
        Returns:
            List of active schedules
        """
        if check_time is None:
            check_time = datetime.utcnow()
        
        schedules = await self.get_active_schedules()
        active_schedules = []
        
        current_day = check_time.weekday()
        current_time_minutes = check_time.hour * 60 + check_time.minute
        
        for schedule in schedules:
            days = schedule.get_days_of_week()
            
            if current_day not in days:
                continue
            
            start_minutes = schedule.get_start_time_minutes()
            end_minutes = schedule.get_end_time_minutes()
            
            if start_minutes <= current_time_minutes < end_minutes:
                active_schedules.append(schedule)
        
        return active_schedules


# Convenience functions
async def create_schedule(
    camera_id: int,
    days_of_week: List[int],
    start_time: str,
    end_time: str,
    db: AsyncSession,
    record_type: str = "continuous",
    is_active: bool = True,
) -> Schedule:
    """Create schedule"""
    service = ScheduleService(db)
    return await service.create_schedule(
        camera_id, days_of_week, start_time, end_time, record_type, is_active
    )


async def update_schedule(
    schedule_id: int,
    db: AsyncSession,
    **kwargs,
) -> Optional[Schedule]:
    """Update schedule"""
    service = ScheduleService(db)
    return await service.update_schedule(schedule_id, **kwargs)


async def delete_schedule(schedule_id: int, db: AsyncSession) -> bool:
    """Delete schedule"""
    service = ScheduleService(db)
    return await service.delete_schedule(schedule_id)


async def get_schedules(
    db: AsyncSession,
    camera_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Schedule]:
    """Get schedules"""
    service = ScheduleService(db)
    return await service.get_schedules(camera_id, is_active, skip, limit)


async def check_schedule(
    camera_id: int,
    db: AsyncSession,
    check_time: Optional[datetime] = None,
) -> Optional[dict]:
    """Check schedule"""
    service = ScheduleService(db)
    return await service.check_schedule(camera_id, check_time)
