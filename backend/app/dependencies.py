"""Dependency injection dependencies"""
from typing import AsyncGenerator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User
from app.core.security import verify_token
from app.config import settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session.
    
    Yields:
        AsyncSession: Database session
    """
    async with get_db() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_current_user(
    token: str = Depends(lambda: None),
) -> Optional[User]:
    """
    Get current user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        Current user or None
        
    Raises:
        HTTPException: If token is invalid
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization token",
        )
    
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization token",
        )
    
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Get user from database
    from app.database import get_db_context
    
    async with get_db_context() as db:
        from sqlalchemy import select
        
        result = await db.execute(
            select(User).where(User.id == int(user_id))
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        
        return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current user
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    return current_user


async def require_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require admin role.
    
    Args:
        current_user: Current user
        
    Returns:
        Current user if admin
        
    Raises:
        HTTPException: If user is not admin
    """
    if not current_user.is_admin():
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    
    return current_user


async def require_viewer(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Require viewer role or higher.
    
    Args:
        current_user: Current user
        
    Returns:
        Current user if viewer or admin
        
    Raises:
        HTTPException: If user is not viewer or admin
    """
    if not (current_user.is_viewer() or current_user.is_admin()):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Viewer privileges required",
        )
    
    return current_user
