from typing import Optional

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt import verify_token
from app.database import get_db

# Import User model (will be created by models branch)
from app.models.user import User
from app.utils.logger import get_logger

logger = get_logger(__name__)

# OAuth2 scheme for extracting bearer tokens
# auto_error=False allows optional authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)


async def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the currently authenticated user.

    Raises HTTPException 401 if not authenticated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    payload = verify_token(token, token_type="access")
    if not payload:
        raise credentials_exception

    user_id = payload.get("sub")
    if not user_id:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )

    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get the authenticated user.

    Returns None if not authenticated (no error raised).
    """
    if not token:
        return None

    payload = verify_token(token, token_type="access")
    if not payload:
        return None

    user_id = payload.get("sub")
    if not user_id:
        return None

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        return None

    return user


async def require_admin(
    user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to require admin privileges.

    Raises HTTPException 403 if user is not an admin.
    """
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return user


async def get_refresh_token_from_cookie(
    refresh_token: Optional[str] = Cookie(None, alias="refresh_token")
) -> Optional[str]:
    """
    Extract refresh token from HttpOnly cookie.
    """
    return refresh_token
