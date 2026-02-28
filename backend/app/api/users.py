"""Users API endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.schemas.common import MessageResponse
from app.services.auth_service import AuthService
from app.api.deps import get_current_user, require_admin, get_pagination
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    """Create a new user
    
    Args:
        user_data: User creation data
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Created user
    """
    auth_service = AuthService(db)
    
    # Check if username exists
    existing = await auth_service.get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )
    
    # Check if email exists
    existing = await auth_service.get_user_by_email(user_data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists",
        )
    
    user = await auth_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
    )
    
    return user


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> List[User]:
    """List all users
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        List of users
    """
    from sqlalchemy import select
    
    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = list(result.scalars().all())
    
    return [UserResponse.model_validate(u.to_dict()) for u in users]


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current user information
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user info
    """
    return UserResponse.model_validate(current_user.to_dict())


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    """Get user by ID
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        User information
        
    Raises:
        HTTPException: If user not found
    """
    auth_service = AuthService(db)
    user = await auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user.to_dict())


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> User:
    """Update user information
    
    Args:
        user_id: User ID
        user_data: User update data
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Updated user
        
    Raises:
        HTTPException: If user not found
    """
    auth_service = AuthService(db)
    user = await auth_service.update_user(
        user_id,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse.model_validate(user.to_dict())


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
) -> MessageResponse:
    """Delete user
    
    Args:
        user_id: User ID
        db: Database session
        current_user: Current authenticated user (must be admin)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If user not found or trying to delete self
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete yourself",
        )
    
    auth_service = AuthService(db)
    success = await auth_service.delete_user(user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return MessageResponse(message="User deleted successfully")
