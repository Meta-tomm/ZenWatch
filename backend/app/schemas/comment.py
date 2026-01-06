from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class CommentTargetType(str, Enum):
    """Type of content being commented on."""
    ARTICLE = "article"
    VIDEO = "video"


class CommentCreate(BaseModel):
    """Create a new comment."""
    content: str = Field(..., min_length=1, max_length=2000)
    target_type: CommentTargetType
    target_id: int
    parent_id: Optional[int] = None  # For replies


class CommentUpdate(BaseModel):
    """Update an existing comment."""
    content: str = Field(..., min_length=1, max_length=2000)


class CommentAuthor(BaseModel):
    """Minimal author info for comments."""
    id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class CommentResponse(BaseModel):
    """Comment response with author info."""
    id: int
    content: str
    target_type: CommentTargetType
    target_id: int
    parent_id: Optional[int] = None
    author: CommentAuthor
    is_edited: bool = False
    is_deleted: bool = False
    created_at: datetime
    updated_at: datetime
    replies_count: int = 0

    class Config:
        from_attributes = True


class CommentWithReplies(CommentResponse):
    """Comment with nested replies."""
    replies: list["CommentResponse"] = []


class PaginatedCommentsResponse(BaseModel):
    """Paginated list of comments."""
    data: list[CommentResponse]
    total: int
    hasMore: bool
    offset: int
    limit: int


# Admin schema
class AdminCommentResponse(CommentResponse):
    """Comment with extra admin fields."""
    author_email: Optional[str] = None
