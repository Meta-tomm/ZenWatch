from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class LoginRequest(BaseModel):
    """Email/password login request"""
    email: EmailStr
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """User registration request"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    """Token refresh request"""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Password reset initiation request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class PasswordChangeRequest(BaseModel):
    """Password change request (authenticated)"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class EmailVerificationRequest(BaseModel):
    """Email verification token request"""
    token: str


class OAuthCallbackRequest(BaseModel):
    """OAuth callback data"""
    provider: Literal['github', 'google', 'discord']
    code: str
    state: Optional[str] = None


class OAuthLinkRequest(BaseModel):
    """Link OAuth provider to existing account"""
    provider: Literal['github', 'google', 'discord']
    code: str
