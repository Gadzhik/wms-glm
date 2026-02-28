"""Recordings API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.recording import (
    RecordingResponse,
    RecordingFilter,
    RecordingExportRequest,
    RecordingExportResponse,
)
from app.schemas.common import MessageResponse
from app.services.recording_service import get_recording_service, RecordingService
from app.api.deps import get_current_user, get_pagination
from app.models.user import User

router = APIRouter(prefix="/recordings", tags=["Recordings"])


@router.get("", response_model=List[RecordingResponse])
async def list_recordings(
    camera_id: int = None,
    recording_type: str = None,
    start_date: str = None,
    end_date: str = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    """List recordings with filtering
    
    Args:
        camera_id: Filter by camera
        recording_type: Filter by recording type
        start_date: Start date filter
        end_date: End date filter
        skip: Number of records to skip
        limit: Maximum number of records
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        List of recordings
    """
    service = get_recording_service(db)
    recordings = await service.get_recordings(
        camera_id=camera_id,
        recording_type=recording_type,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )
    
    return [r.to_dict() for r in recordings]


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get recording by ID
    
    Args:
        recording_id: Recording ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Recording information
        
    Raises:
        HTTPException: If recording not found
    """
    service = get_recording_service(db)
    recording = await service.get_recording(recording_id)
    
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found",
        )
    
    return recording.to_dict()


@router.delete("/{recording_id}", response_model=MessageResponse)
async def delete_recording(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """Delete recording
    
    Args:
        recording_id: Recording ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If recording not found
    """
    service = get_recording_service(db)
    success = await service.delete_recording(recording_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found",
        )
    
    return MessageResponse(message="Recording deleted successfully")


@router.post("/{recording_id}/export", response_model=RecordingExportResponse)
async def export_recording(
    recording_id: int,
    export_data: RecordingExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RecordingExportResponse:
    """Export recording to file
    
    Args:
        recording_id: Recording ID
        export_data: Export configuration
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Export information
        
    Raises:
        HTTPException: If recording not found or export fails
    """
    import os
    import uuid
    from datetime import datetime, timedelta
    
    service = get_recording_service(db)
    recording = await service.get_recording(recording_id)
    
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found",
        )
    
    # Generate export ID and output path
    export_id = str(uuid.uuid4())
    from app.config import settings
    output_path = service.get_export_path(export_id)
    
    # Export recording
    success = await service.export_recording(
        recording_id,
        output_path,
        export_data.start_time,
        export_data.end_time,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export failed",
        )
    
    # Calculate expiration time (24 hours)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    return RecordingExportResponse(
        export_id=export_id,
        status="completed",
        file_url=f"/exports/{export_id}.mp4",
        file_size=os.path.getsize(output_path) if os.path.exists(output_path) else 0,
        expires_at=expires_at,
    )


@router.get("/{recording_id}/metadata")
async def get_recording_metadata(
    recording_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get recording metadata
    
    Args:
        recording_id: Recording ID
        db: Database session
        current_user: Current authenticated user
        
    Returns:
        Recording metadata
        
    Raises:
        HTTPException: If recording not found
    """
    service = get_recording_service(db)
    metadata = await service.get_recording_metadata(recording_id)
    
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording metadata not found",
        )
    
    return metadata.to_dict()
