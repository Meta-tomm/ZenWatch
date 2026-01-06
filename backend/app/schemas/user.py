from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user fields."""
    email: EmailStr
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    """Fields for creating a new user."""
    password: str = Field(..., min_length=8, max_length=128)


class UserUpdate(BaseModel):
    """Fields that can be updated by the user."""
    username: Optional[str] = Field(None, min_length=3, max_length=50, pattern=r'^[a-zA-Z0-9_-]+$')
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None


class UserResponse(BaseModel):
    """Public user response."""
    id: int
    email: EmailStr
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserPublicProfile(BaseModel):
    """Public profile visible to other users."""
    id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserExportData(BaseModel):
    """GDPR data export format."""
    user: UserResponse
    keywords: list["UserKeywordResponse"]
    comments: list["CommentResponse"]
    article_states: list[dict]
    video_states: list[dict]
    consents: list[dict]
    export_date: datetime


class AdminUserUpdate(BaseModel):
    """Admin-only user update fields."""
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)


class PaginatedUsersResponse(BaseModel):
    """Paginated list of users for admin."""
    data: list[UserResponse]
    total: int
    hasMore: bool
    offset: int
    limit: int


# Forward references for circular imports
from app.schemas.comment import CommentResponse
from app.schemas.user_keyword import UserKeywordResponse

UserExportData.model_rebuild()
