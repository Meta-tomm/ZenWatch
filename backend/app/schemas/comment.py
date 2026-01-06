"""Comment schemas for article and video discussions"""

from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, model_validator

from app.schemas.user import UserPublicProfile


class CommentCreate(BaseModel):
    """Schema for creating a new comment"""

    content: str = Field(..., min_length=1, max_length=5000)
    article_id: Optional[int] = None
    video_id: Optional[int] = None
    parent_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_target(self):
        if self.article_id is None and self.video_id is None:
            raise ValueError("Either article_id or video_id must be provided")
        if self.article_id is not None and self.video_id is not None:
            raise ValueError("Cannot comment on both article and video")
        return self


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""

    content: str = Field(..., min_length=1, max_length=5000)


class CommentResponse(BaseModel):
    """Schema for comment API response"""

    id: int
    user_id: Optional[UUID] = None
    user: Optional[UserPublicProfile] = None
    article_id: Optional[int] = None
    video_id: Optional[int] = None
    parent_id: Optional[int] = None
    content: str
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    reply_count: int = 0

    class Config:
        from_attributes = True


class CommentThread(BaseModel):
    """Schema for comment with nested replies"""

    id: int
    user_id: Optional[UUID] = None
    user: Optional[UserPublicProfile] = None
    article_id: Optional[int] = None
    video_id: Optional[int] = None
    parent_id: Optional[int] = None
    content: str
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    replies: List["CommentThread"] = []

    class Config:
        from_attributes = True


class PaginatedCommentsResponse(BaseModel):
    """Schema for paginated comments list"""

    data: List[CommentResponse]
    total: int
    has_more: bool
    offset: int
    limit: int
