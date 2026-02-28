"""Security utilities for JWT tokens and password hashing"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
import bcrypt

from app.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password
    """
    # Encode password to bytes
    password_bytes = password.encode('utf-8')
    # Generate salt and hash
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Encode to bytes
        plain_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        # Verify
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Get password hash (alias for hash_password)"""
    return hash_password(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token
    
    Args:
        data: Payload data to encode
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT refresh token
    
    Args:
        data: Payload data to encode
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify and decode a JWT token
    
    Args:
        token: JWT token to verify
        
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode an access token
    
    Args:
        token: Access token to decode
        
    Returns:
        Decoded token payload if valid and is access token, None otherwise
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "access":
        return payload
    return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a refresh token
    
    Args:
        token: Refresh token to decode
        
    Returns:
        Decoded token payload if valid and is refresh token, None otherwise
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None


def get_token_expiry(token: str) -> Optional[datetime]:
    """Get token expiration time
    
    Args:
        token: JWT token
        
    Returns:
        Expiration datetime or None if invalid
    """
    payload = verify_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None


def is_token_expired(token: str) -> bool:
    """Check if token is expired
    
    Args:
        token: JWT token
        
    Returns:
        True if expired, False otherwise
    """
    expiry = get_token_expiry(token)
    if expiry is None:
        return True
    return datetime.utcnow() > expiry


def create_token_pair(user_id: int, username: str, role: str) -> tuple[str, str]:
    """Create access and refresh token pair
    
    Args:
        user_id: User ID
        username: Username
        role: User role
        
    Returns:
        Tuple of (access_token, refresh_token)
    """
    token_data = {
        "sub": str(user_id),
        "username": username,
        "role": role
    }
    
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return access_token, refresh_token
