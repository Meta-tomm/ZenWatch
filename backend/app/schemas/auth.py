"""Authentication schemas for login, registration, and tokens"""

from typing import Optional, Literal
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class LoginRequest(BaseModel):
    """Schema for email/password login"""

    email: EmailStr
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    """Schema for user registration"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores and hyphens")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class TokenResponse(BaseModel):
    """Schema for JWT token response"""

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenPayload(BaseModel):
    """Schema for JWT token payload (internal use)"""

    sub: UUID
    email: str
    role: str = "user"
    exp: datetime
    iat: datetime
    type: Literal["access", "refresh"] = "access"


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh"""

    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class PasswordChangeRequest(BaseModel):
    """Schema for authenticated password change"""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class OAuthCallbackRequest(BaseModel):
    """Schema for OAuth callback"""

    code: str
    state: Optional[str] = None


class OAuthAccountResponse(BaseModel):
    """Schema for OAuth account info"""

    id: int
    provider: str
    provider_email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
