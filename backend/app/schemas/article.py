from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator


class ArticleCreate(BaseModel):
    # Champs obligatoires
    title: str = Field(..., min_length=1, max_length=500)
    url: str = Field(..., pattern=r'^https?://')
    published_at: datetime

    # Champs optionnels
    content: Optional[str] = Field(None, max_length=50000)
    author: Optional[str] = None
    upvotes: Optional[int] = 0
    comments_count: Optional[int] = 0
    tags: Optional[List[str]] = []
    language: Optional[str] = 'en'
    read_time_minutes: Optional[int] = None

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v


class ArticleResponse(ArticleCreate):
    id: int
    source_id: Optional[int] = None
    source_type: Optional[str] = None
    external_id: Optional[str] = None
    score: Optional[float] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    scraped_at: Optional[datetime] = None
    is_read: bool = False
    is_favorite: bool = False
    is_archived: bool = False
    is_liked: bool = False
    is_disliked: bool = False
    # Computed fields for frontend compatibility
    likes: int = 0
    dislikes: int = 0
    user_reaction: Optional[str] = None
    video_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    view_count: Optional[int] = None
    is_video: Optional[bool] = False
    created_at: datetime
    updated_at: datetime

    @model_validator(mode='after')
    def compute_reaction_fields(self):
        # Derive computed fields from is_liked/is_disliked booleans
        self.likes = 1 if self.is_liked else 0
        self.dislikes = 1 if self.is_disliked else 0
        if self.is_liked:
            self.user_reaction = 'like'
        elif self.is_disliked:
            self.user_reaction = 'dislike'
        else:
            self.user_reaction = None
        return self

    class Config:
        from_attributes = True


class VideoResponse(BaseModel):
    id: int
    title: str
    url: str
    video_id: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = None
    view_count: Optional[int] = None
    author: Optional[str] = None
    published_at: datetime
    score: Optional[float] = None
    category: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = []
    is_read: bool = False
    is_favorite: bool = False
    is_liked: bool = False
    is_disliked: bool = False
    # Computed fields for frontend compatibility
    likes: int = 0
    dislikes: int = 0
    user_reaction: Optional[str] = None
    source_type: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @model_validator(mode='after')
    def compute_reaction_fields(self):
        # Derive computed fields from is_liked/is_disliked booleans
        self.likes = 1 if self.is_liked else 0
        self.dislikes = 1 if self.is_disliked else 0
        if self.is_liked:
            self.user_reaction = 'like'
        elif self.is_disliked:
            self.user_reaction = 'dislike'
        else:
            self.user_reaction = None
        return self

    class Config:
        from_attributes = True


class PaginatedArticlesResponse(BaseModel):
    data: List[ArticleResponse]
    total: int
    hasMore: bool
    offset: int
    limit: int


class PaginatedVideosResponse(BaseModel):
    data: List[VideoResponse]
    total: int
    hasMore: bool
    offset: int
    limit: int
