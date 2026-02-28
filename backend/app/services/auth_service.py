"""Authentication service for user management and JWT tokens"""
from typing import Optional, Tuple
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.config import settings


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: AsyncSession):
        """Initialize auth service
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def authenticate(
        self,
        username: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate user with username and password
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User if authentication successful, None otherwise
        """
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow().isoformat()
        await self.db.commit()
        
        return user
    
    async def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "viewer",
    ) -> User:
        """Create a new user
        
        Args:
            username: Username
            email: Email address
            password: Plain text password
            role: User role (admin or viewer)
            
        Returns:
            Created user
        """
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=role,
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID
        
        Args:
            user_id: User ID
            
        Returns:
            User or None
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username
        
        Args:
            username: Username
            
        Returns:
            User or None
        """
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email
        
        Args:
            email: Email address
            
        Returns:
            User or None
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update_user(
        self,
        user_id: int,
        email: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[str] = None,
    ) -> Optional[User]:
        """Update user information
        
        Args:
            user_id: User ID
            email: New email
            password: New password
            role: New role
            
        Returns:
            Updated user or None
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        if email:
            user.email = email
        
        if password:
            user.password_hash = hash_password(password)
        
        if role:
            user.role = role
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete user
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        
        return True
    
    def create_token_pair(self, user: User) -> Tuple[str, str, int]:
        """Create access and refresh token pair
        
        Args:
            user: User object
            
        Returns:
            Tuple of (access_token, refresh_token, expires_in)
        """
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "role": user.role,
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        
        return access_token, refresh_token, expires_in
    
    async def verify_refresh_token(
        self,
        refresh_token: str,
    ) -> Optional[User]:
        """Verify refresh token and get user
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            User if valid, None otherwise
        """
        payload = verify_token(refresh_token)
        if not payload:
            return None
        
        if payload.get("type") != "refresh":
            return None
        
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        return await self.get_user_by_id(int(user_id))
    
    async def update_refresh_token(
        self,
        user_id: int,
        refresh_token: str,
    ) -> bool:
        """Update user's refresh token
        
        Args:
            user_id: User ID
            refresh_token: New refresh token
            
        Returns:
            True if updated
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.refresh_token = refresh_token
        await self.db.commit()
        
        return True


# Convenience functions
async def authenticate_user(
    username: str,
    password: str,
    db: AsyncSession,
) -> Optional[User]:
    """Authenticate user
    
    Args:
        username: Username
        password: Password
        db: Database session
        
    Returns:
        User if authenticated, None otherwise
    """
    service = AuthService(db)
    return await service.authenticate(username, password)


async def create_user(
    username: str,
    email: str,
    password: str,
    role: str = "viewer",
    db: Optional[AsyncSession] = None,
) -> User:
    """Create a new user
    
    Args:
        username: Username
        email: Email
        password: Password
        role: User role
        db: Database session
        
    Returns:
        Created user
    """
    from app.database import get_db_context
    
    if db is None:
        async with get_db_context() as session:
            service = AuthService(session)
            return await service.create_user(username, email, password, role)
    else:
        service = AuthService(db)
        return await service.create_user(username, email, password, role)


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token
    
    Args:
        token: JWT token
        
    Returns:
        Token payload if valid, None otherwise
    """
    from app.core.security import verify_token as _verify_token
    return _verify_token(token)
