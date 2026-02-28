"""User-related Pydantic schemas"""
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    role: str = Field(
        default="viewer",
        pattern="^(admin|viewer)$",
        description="User role (admin or viewer)"
    )


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 characters)"
    )


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = Field(None, description="Email address")
    password: Optional[str] = Field(None, min_length=8, max_length=100, description="New password")
    role: Optional[str] = Field(None, pattern="^(admin|viewer)$", description="User role")


class UserResponse(BaseModel):
    """Schema for user response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    role: str = Field(..., description="User role")
    created_at: str = Field(..., description="Account creation timestamp")
    last_login: Optional[str] = Field(None, description="Last login timestamp")


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class TokenRefresh(BaseModel):
    """Schema for token refresh"""
    refresh_token: str = Field(..., description="Refresh token")


class PasswordChange(BaseModel):
    """Schema for password change"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="New password (min 8 characters)"
    )
