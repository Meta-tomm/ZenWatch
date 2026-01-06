"""Authentication API routes"""
import secrets
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from app.database import get_db
from app.auth.jwt import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from app.auth.password import hash_password, verify_password
from app.auth.deps import get_current_user
from app.auth.oauth import (
    get_oauth_provider,
    build_authorize_url,
    exchange_code_for_token,
    get_oauth_user_info,
    get_github_email,
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


# Pydantic schemas for auth
class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 900  # 15 minutes in seconds


class MessageResponse(BaseModel):
    """Simple message response"""
    message: str


class OAuthRedirectResponse(BaseModel):
    """OAuth redirect response"""
    authorize_url: str
    state: str


# Store OAuth states temporarily (in production, use Redis)
oauth_states: dict[str, dict] = {}


@router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Register a new user with email and password

    - Creates a new user account
    - Returns access token and sets refresh token in HttpOnly cookie
    """
    from app.models.user import User

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists (if provided)
    if user_data.username:
        existing_username = db.query(User).filter(User.username == user_data.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

    # Create new user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        username=user_data.username,
        display_name=user_data.display_name or user_data.username,
        is_active=True,
        role="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    logger.info(f"New user registered: {user.email}")

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password (OAuth2 form)

    - Validates credentials
    - Returns access token and sets refresh token in HttpOnly cookie
    """
    from app.models.user import User

    # Find user by email (form_data.username contains the email)
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user has a password (might be OAuth-only)
    if not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please login with your OAuth provider",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    logger.info(f"User logged in: {user.email}")

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)


@router.post("/auth/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    current_user = Depends(get_current_user)
):
    """
    Logout current user

    - Clears refresh token cookie
    """
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True,
        samesite="lax",
    )

    logger.info(f"User logged out: {current_user.email}")

    return MessageResponse(message="Successfully logged out")


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token from cookie

    - Validates refresh token
    - Returns new access token
    """
    from app.models.user import User

    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify refresh token
    payload = verify_refresh_token(refresh_token)
    if not payload:
        response.delete_cookie(key="refresh_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()

    if not user or not user.is_active:
        response.delete_cookie(key="refresh_token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or disabled",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate new access token
    access_token = create_access_token(data={"sub": str(user.id)})

    return TokenResponse(access_token=access_token)


@router.get("/auth/oauth/{provider}", response_model=OAuthRedirectResponse)
async def oauth_redirect(
    provider: str,
    request: Request,
):
    """
    Get OAuth authorization URL for a provider

    - Returns URL to redirect user for OAuth login
    - Generates state token for CSRF protection
    """
    oauth_provider = get_oauth_provider(provider)
    if not oauth_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )

    if not oauth_provider.client_id or not oauth_provider.client_secret:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"OAuth provider {provider} is not configured"
        )

    # Generate state token
    state = secrets.token_urlsafe(32)

    # Build redirect URI
    redirect_uri = str(request.url_for("oauth_callback", provider=provider))

    # Store state temporarily
    oauth_states[state] = {
        "provider": provider,
        "redirect_uri": redirect_uri,
        "created_at": datetime.utcnow(),
    }

    # Build authorization URL
    authorize_url = build_authorize_url(oauth_provider, redirect_uri, state)

    return OAuthRedirectResponse(authorize_url=authorize_url, state=state)


@router.get("/auth/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    response: Response = None,
    db: Session = Depends(get_db),
):
    """
    Handle OAuth callback from provider

    - Exchanges code for tokens
    - Creates or updates user account
    - Returns access token
    """
    from app.models.user import User
    from app.models.oauth_account import OAuthAccount

    # Check for errors from provider
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth error: {error}"
        )

    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing code or state parameter"
        )

    # Validate state
    state_data = oauth_states.pop(state, None)
    if not state_data or state_data["provider"] != provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid state parameter"
        )

    oauth_provider = get_oauth_provider(provider)
    if not oauth_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported OAuth provider: {provider}"
        )

    # Exchange code for token
    token_data = await exchange_code_for_token(
        oauth_provider,
        code,
        state_data["redirect_uri"]
    )

    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange code for token"
        )

    oauth_access_token = token_data.get("access_token")
    if not oauth_access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No access token in response"
        )

    # Get user info from provider
    user_info = await get_oauth_user_info(oauth_provider, oauth_access_token)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get user info from provider"
        )

    # GitHub: get email separately if not provided
    email = user_info.get("email")
    if provider == "github" and not email:
        email = await get_github_email(oauth_access_token)

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not provided by OAuth provider"
        )

    provider_id = user_info.get("provider_id")
    if not provider_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provider ID not found"
        )

    # Check if OAuth account already exists
    oauth_account = db.query(OAuthAccount).filter(
        OAuthAccount.provider == provider,
        OAuthAccount.provider_user_id == provider_id
    ).first()

    user = None

    if oauth_account:
        # Existing OAuth account - get user
        user = oauth_account.user
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is disabled"
            )
    else:
        # Check if user exists with this email
        user = db.query(User).filter(User.email == email).first()

        if user:
            # Link OAuth account to existing user
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_user_id=provider_id,
                access_token=oauth_access_token,
            )
            db.add(oauth_account)
        else:
            # Create new user
            username = user_info.get("username")
            if username:
                # Check if username is taken
                existing = db.query(User).filter(User.username == username).first()
                if existing:
                    username = f"{username}_{provider_id[:8]}"

            user = User(
                email=email,
                username=username,
                display_name=user_info.get("name"),
                avatar_url=user_info.get("avatar_url"),
                is_active=True,
                role="user",
            )
            db.add(user)
            db.flush()  # Get user.id

            # Create OAuth account
            oauth_account = OAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_user_id=provider_id,
                access_token=oauth_access_token,
            )
            db.add(oauth_account)

            logger.info(f"New user registered via OAuth ({provider}): {email}")

    # Update last login
    user.last_login_at = datetime.utcnow()
    db.commit()

    logger.info(f"User logged in via OAuth ({provider}): {user.email}")

    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Set refresh token in HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return TokenResponse(access_token=access_token)
