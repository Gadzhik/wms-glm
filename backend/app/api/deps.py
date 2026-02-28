"""API dependencies for dependency injection"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app.models.user import User
from app.core.security import verify_token
from app.config import settings


security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Optional[User]:
    """Get current user from JWT token
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Current user or None
        
    Raises:
        HTTPException: If token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    if not token:
        raise credentials_exception
    
    payload = verify_token(token)
    if not payload:
        raise credentials_exception
    
    if payload.get("type") != "access":
        raise credentials_exception
    
    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception
    
    # Get user from database
    from app.database import get_db_context
    
    async with get_db_context() as db:
        from sqlalchemy import select
        result = await db.execute(select(User).where(User.id == int(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise credentials_exception
        
        return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If user is not found
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
    """Require admin role
    
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
    """Require viewer role or higher
    
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


class PaginationParams:
    """Pagination parameters"""
    
    def __init__(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        """Initialize pagination parameters
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records
        """
        self.skip = skip
        self.limit = min(limit, 1000)  # Max 1000 records per request
    
    @property
    def page(self) -> int:
        """Get current page number (1-indexed)"""
        return (self.skip // self.limit) + 1
    
    @property
    def total_pages(self, total: int) -> int:
        """Get total number of pages
        
        Args:
            total: Total number of records
            
        Returns:
            Total pages
        """
        return (total + self.limit - 1) // self.limit


async def get_pagination(
    skip: int = 0,
    limit: int = 100,
) -> PaginationParams:
    """Get pagination parameters
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        
    Returns:
        PaginationParams instance
    """
    return PaginationParams(skip, limit)
