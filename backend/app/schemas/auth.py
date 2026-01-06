from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request body for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')


class LoginRequest(BaseModel):
    """Request body for user login."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response containing access token."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class AuthResponse(BaseModel):
    """Full auth response with user info."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class RefreshResponse(BaseModel):
    """Response from token refresh."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class OAuthRedirectResponse(BaseModel):
    """Response with OAuth redirect URL."""
    authorization_url: str


class PasswordResetRequest(BaseModel):
    """Request to initiate password reset."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Request to confirm password reset."""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


# Import at end to avoid circular dependency
from app.schemas.user import UserResponse

AuthResponse.model_rebuild()
