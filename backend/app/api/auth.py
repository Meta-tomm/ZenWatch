import secrets
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, get_refresh_token_from_cookie
from app.auth.jwt import create_access_token, create_refresh_token, verify_token
from app.auth.oauth import get_oauth_provider
from app.auth.password import hash_password, verify_password
from app.config import settings
from app.database import get_db

# Import models (will be created by models branch)
from app.models.user import OAuthAccount, User
from app.schemas.auth import (
    AuthResponse,
    OAuthRedirectResponse,
    RefreshResponse,
    RegisterRequest,
)
from app.schemas.user import UserResponse
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

# Store OAuth states temporarily (in production, use Redis)
_oauth_states: dict[str, str] = {}


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email/password.

    Returns access token and user info.
    """
    # Check if email already exists
    existing = db.query(User).filter(User.email == request.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Check if username already exists (if provided)
    if request.username:
        existing_username = db.query(User).filter(User.username == request.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken"
            )

    # Create user
    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        username=request.username,
        is_active=True,
        is_admin=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"New user registered: {user.email}")

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email/password (OAuth2 form).

    Returns access token and user info.
    """
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    logger.info(f"User logged in: {user.email}")

    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return AuthResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """
    Get current authenticated user info.
    """
    return UserResponse.model_validate(user)


@router.patch("/profile", response_model=UserResponse)
async def update_profile(
    updates: dict,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user profile.

    Allowed fields: username, display_name, bio, avatar_url
    """
    allowed_fields = {"username", "display_name", "bio", "avatar_url"}

    for field, value in updates.items():
        if field in allowed_fields:
            # Check username uniqueness
            if field == "username" and value:
                existing = db.query(User).filter(
                    User.username == value,
                    User.id != user.id
                ).first()
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Username already taken"
                    )
            setattr(user, field, value)

    db.commit()
    db.refresh(user)
    logger.info(f"Profile updated: {user.email}")
    return UserResponse.model_validate(user)


@router.post("/logout")
async def logout(
    response: Response,
    user: User = Depends(get_current_user)
):
    """
    Logout the current user.

    Clears the refresh token cookie.
    """
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
    )

    logger.info(f"User logged out: {user.email}")
    return {"message": "Successfully logged out"}


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(
    response: Response,
    refresh_token: Optional[str] = Depends(get_refresh_token_from_cookie),
    db: Session = Depends(get_db)
):
    """
    Refresh the access token using refresh token from cookie.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    payload = verify_token(refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    # Generate new tokens
    new_access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})

    # Update refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return RefreshResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get("/oauth/{provider}")
async def oauth_redirect(provider: str, request: Request):
    """
    Redirect to OAuth provider authorization page.

    Supported providers: github, google, discord
    """
    oauth = get_oauth_provider(provider)
    if not oauth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' not configured"
        )

    # Generate state for CSRF protection
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = provider

    # Build redirect URI
    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/{provider}"

    authorization_url = oauth.get_authorization_url(redirect_uri, state)

    return RedirectResponse(url=authorization_url)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: str,
    state: str,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Handle OAuth callback from provider.

    Creates or links account and returns tokens.
    """
    # Verify state
    stored_provider = _oauth_states.pop(state, None)
    if stored_provider != provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth state"
        )

    oauth = get_oauth_provider(provider)
    if not oauth:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' not configured"
        )

    redirect_uri = f"{settings.FRONTEND_URL}/auth/callback/{provider}"

    # Exchange code for token
    access_token = await oauth.exchange_code(code, redirect_uri)
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange OAuth code"
        )

    # Get user info from provider
    user_info = await oauth.get_user_info(access_token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from provider"
        )

    # Check if OAuth account already exists
    oauth_account = db.query(OAuthAccount).filter(
        OAuthAccount.provider == provider,
        OAuthAccount.provider_user_id == user_info.provider_user_id
    ).first()

    if oauth_account:
        # Existing OAuth account - login
        user = oauth_account.user
    elif user_info.email:
        # Check if user with this email exists
        user = db.query(User).filter(User.email == user_info.email).first()
        if user:
            # Link OAuth account to existing user
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_user_id=user_info.provider_user_id,
            )
            db.add(oauth_account)
        else:
            # Create new user
            user = User(
                email=user_info.email,
                username=user_info.username,
                display_name=user_info.display_name,
                avatar_url=user_info.avatar_url,
                is_active=True,
                is_admin=False,
            )
            db.add(user)
            db.flush()

            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_user_id=user_info.provider_user_id,
            )
            db.add(oauth_account)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by OAuth provider"
        )

    db.commit()
    db.refresh(user)

    logger.info(f"OAuth login: {user.email} via {provider}")

    # Generate tokens
    jwt_access_token = create_access_token({"sub": str(user.id)})
    jwt_refresh_token = create_refresh_token({"sub": str(user.id)})

    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=jwt_refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT != "development",
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return AuthResponse(
        access_token=jwt_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user),
    )
