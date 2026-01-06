from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=8, max_length=128)

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


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Username must contain only alphanumeric characters, underscores, and hyphens')
        return v


class UserResponse(BaseModel):
    """Full user response schema"""
    id: UUID
    email: EmailStr
    username: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPublicProfile(BaseModel):
    """Public user profile (limited fields)"""
    id: UUID
    username: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class OAuthAccountResponse(BaseModel):
    """OAuth account response schema"""
    id: int
    provider: str
    provider_email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserWithOAuth(UserResponse):
    """User response with linked OAuth accounts"""
    oauth_accounts: List[OAuthAccountResponse] = []
