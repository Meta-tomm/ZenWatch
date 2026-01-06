"""User schemas for API request/response validation"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, field_validator
import re


class UserBase(BaseModel):
    """Base user fields shared across schemas"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores and hyphens")
        return v


class UserCreate(UserBase):
    """Schema for user registration"""

    password: str = Field(..., min_length=8, max_length=100)

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


class UserUpdate(BaseModel):
    """Schema for updating user profile"""

    username: Optional[str] = Field(None, min_length=3, max_length=50)
    avatar_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores and hyphens")
        return v


class UserResponse(BaseModel):
    """Schema for user API responses"""

    id: UUID
    email: EmailStr
    username: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    role: str = "user"
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPublicProfile(BaseModel):
    """Schema for public user profile (limited info)"""

    id: UUID
    username: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserKeywordCreate(BaseModel):
    """Schema for creating user keywords"""

    keyword: str = Field(..., min_length=1, max_length=100)
    weight: float = Field(default=1.0, ge=0.1, le=5.0)


class UserKeywordResponse(BaseModel):
    """Schema for user keyword response"""

    id: int
    keyword: str
    weight: float
    created_at: datetime

    class Config:
        from_attributes = True


class UserKeywordsListResponse(BaseModel):
    """Schema for list of user keywords"""

    keywords: List[UserKeywordResponse]
    total: int
