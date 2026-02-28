"""Events API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.event import (
    EventResponse,
    EventFilter,
    EventAcknowledgeRequest,
    EventStats,
)
from app.schemas.common import MessageResponse
from app.models.event import Event
from app.api.deps import get_current_user, get_pagination
from app.models.user import User

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=List[EventResponse])
async def list_events(
    event_type: str = None,
    camera_id: int = None,
    status_filter: str = None,
    start_date: str = None,
    end_date: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """List events with filtering
    
    Args:
        event_type: Filter by event type
        camera_id: Filter by camera
        status_filter: Filter by status
        start_date: Start date filter
        end_date: End date filter
        skip: Number of records to skip
        limit: Maximum number of records
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of events
    """
    from sqlalchemy import select
    
    query = select(Event)
    
    if event_type:
        query = query.where(Event.event_type == event_type)
    
    if camera_id:
        query = query.where(Event.camera_id == camera_id)
    
    if status_filter:
        query = query.where(Event.status == status_filter)
    
    if start_date:
        query = query.where(Event.timestamp >= start_date)
    
    if end_date:
        query = query.where(Event.timestamp <= end_date)
    
    query = query.order_by(Event.timestamp.desc())
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    events = list(result.scalars().all())
    
    return [e.to_dict() for e in events]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get event by ID
    
    Args:
        event_id: Event ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Event information
        
    Raises:
        HTTPException: If event not found
    """
    from sqlalchemy import select
    
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    return event.to_dict()


@router.post("/{event_id}/acknowledge", response_model=MessageResponse)
async def acknowledge_event(
    event_id: int,
    ack_data: EventAcknowledgeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Acknowledge event(s)
    
    Args:
        event_id: Event ID (or use request body for multiple)
        ack_data: Acknowledgment data
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If event not found
    """
    from sqlalchemy import select
    
    # Get event
    result = await db.execute(
        select(Event).where(Event.id == event_id)
    )
    event = result.scalar_one_or_none()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    
    # Acknowledge event
    event.acknowledge()
    await db.commit()
    
    return MessageResponse(message="Event acknowledged successfully")


@router.post("/acknowledge", response_model=MessageResponse)
async def acknowledge_events(
    ack_data: EventAcknowledgeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Acknowledge multiple events
    
    Args:
        ack_data: Acknowledgment data with event IDs
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    from sqlalchemy import select
    
    for event_id in ack_data.event_ids:
        result = await db.execute(
            select(Event).where(Event.id == event_id)
        )
        event = result.scalar_one_or_none()
        
        if event:
            event.acknowledge()
    
    await db.commit()
    
    return MessageResponse(
        message=f"Acknowledged {len(ack_data.event_ids)} events"
    )


@router.get("/stats", response_model=EventStats)
async def get_event_stats(
    camera_id: int = None,
    start_date: str = None,
    end_date: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get event statistics
    
    Args:
        camera_id: Filter by camera
        start_date: Start date filter
        end_date: End date filter
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Event statistics
    """
    from sqlalchemy import select, func
    
    query = select(Event)
    
    if camera_id:
        query = query.where(Event.camera_id == camera_id)
    
    if start_date:
        query = query.where(Event.timestamp >= start_date)
    
    if end_date:
        query = query.where(Event.timestamp <= end_date)
    
    result = await db.execute(query)
    events = list(result.scalars().all())
    
    # Calculate stats
    total_events = len(events)
    by_type = {}
    by_status = {}
    by_camera = {}
    new_events = 0
    acknowledged_events = 0
    resolved_events = 0
    
    for event in events:
        # Count by type
        event_type = event.event_type
        by_type[event_type] = by_type.get(event_type, 0) + 1
        
        # Count by status
        status = event.status
        by_status[status] = by_status.get(status, 0) + 1
        
        # Count by camera
        if event.camera_id:
            by_camera[event.camera_id] = by_camera.get(event.camera_id, 0) + 1
        
        # Count by status
        if event.is_new():
            new_events += 1
        elif event.is_acknowledged():
            acknowledged_events += 1
        elif event.is_resolved():
            resolved_events += 1
    
    return {
        "total_events": total_events,
        "by_type": by_type,
        "by_status": by_status,
        "by_camera": by_camera,
        "new_events": new_events,
        "acknowledged_events": acknowledged_events,
        "resolved_events": resolved_events,
        "oldest_event": events[-1].timestamp if events else None,
        "newest_event": events[0].timestamp if events else None,
    }
