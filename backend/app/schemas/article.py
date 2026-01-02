from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator


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
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaginatedArticlesResponse(BaseModel):
    data: List[ArticleResponse]
    total: int
    hasMore: bool
    offset: int
    limit: int
