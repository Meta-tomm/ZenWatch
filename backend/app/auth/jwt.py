"""JWT token utilities for authentication"""
from datetime import datetime, timedelta
from typing import Any, Optional

from jose import JWTError, jwt

from app.config import settings


# Token expiration times
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Algorithm for JWT
ALGORITHM = "HS256"


def create_access_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new access token

    Args:
        data: Payload data (should include "sub" with user ID)
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(
    data: dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new refresh token

    Args:
        data: Payload data (should include "sub" with user ID)
        expires_delta: Custom expiration time

    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict[str, Any]]:
    """
    Verify and decode a JWT token

    Args:
        token: JWT token string

    Returns:
        Decoded payload if valid, None if invalid or expired

    Raises:
        JWTError: If token is invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_refresh_token(token: str) -> Optional[dict[str, Any]]:
    """
    Verify a refresh token specifically

    Args:
        token: JWT refresh token string

    Returns:
        Decoded payload if valid refresh token, None otherwise
    """
    payload = verify_token(token)
    if payload and payload.get("type") == "refresh":
        return payload
    return None
