"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.user import UserLogin, TokenResponse, TokenRefresh, PasswordChange
from app.services.auth_service import AuthService
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login user and return JWT tokens
    
    Args:
        credentials: Login credentials
        db: Database session
        
    Returns:
        Token response with access and refresh tokens
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    user = await auth_service.authenticate(credentials.username, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token, refresh_token, expires_in = auth_service.create_token_pair(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user.to_dict(),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Refresh access token using refresh token
    
    Args:
        token_data: Refresh token
        db: Database session
        
    Returns:
        New token response
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    auth_service = AuthService(db)
    user = await auth_service.verify_refresh_token(token_data.refresh_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    access_token, refresh_token, expires_in = auth_service.create_token_pair(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user.to_dict(),
    )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Logout user (invalidate refresh token)
    
    Args:
        current_user: Current user
        db: Database session
    """
    auth_service = AuthService(db)
    await auth_service.update_refresh_token(current_user.id, None)


@router.post("/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Change user password
    
    Args:
        password_data: Password change data
        current_user: Current user
        db: Database session
        
    Raises:
        HTTPException: If old password is incorrect
    """
    from app.core.security import verify_password
    
    # Verify old password
    if not verify_password(password_data.old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )
    
    # Update password
    await auth_service.update_user(
        current_user.id,
        password=password_data.new_password,
    )


@router.get("/me", response_model=dict)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> dict:
    """Get current user information
    
    Args:
        current_user: Current user
        
    Returns:
        User information
    """
    return current_user.to_dict()
