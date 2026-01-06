from typing import Optional, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, model_validator


class CommentCreate(BaseModel):
    """Schema for creating a new comment"""
    article_id: Optional[int] = None
    video_id: Optional[int] = None
    parent_id: Optional[int] = None
    content: str = Field(..., min_length=1, max_length=5000)

    @model_validator(mode='after')
    def validate_target(self):
        if self.article_id is None and self.video_id is None:
            raise ValueError('Either article_id or video_id must be provided')
        if self.article_id is not None and self.video_id is not None:
            raise ValueError('Cannot specify both article_id and video_id')
        return self


class CommentUpdate(BaseModel):
    """Schema for updating a comment"""
    content: str = Field(..., min_length=1, max_length=5000)


class CommentAuthor(BaseModel):
    """Minimal author info for comment responses"""
    id: UUID
    username: str
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Single comment response"""
    id: int
    user_id: Optional[UUID] = None
    article_id: Optional[int] = None
    video_id: Optional[int] = None
    parent_id: Optional[int] = None
    content: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    author: Optional[CommentAuthor] = None
    reply_count: int = 0

    class Config:
        from_attributes = True


class CommentThread(BaseModel):
    """Comment with nested replies"""
    id: int
    user_id: Optional[UUID] = None
    article_id: Optional[int] = None
    video_id: Optional[int] = None
    parent_id: Optional[int] = None
    content: str
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    author: Optional[CommentAuthor] = None
    replies: List['CommentThread'] = []

    class Config:
        from_attributes = True


class PaginatedCommentsResponse(BaseModel):
    """Paginated comments response"""
    data: List[CommentResponse]
    total: int
    has_more: bool
    offset: int
    limit: int
