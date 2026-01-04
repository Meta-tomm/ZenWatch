from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field, field_validator


class ScrapedArticle(BaseModel):
    """
    Validated article data from scrapers, before DB insertion

    This schema ensures all scraped data is validated and normalized
    before being saved to the database.
    """

    # Core fields (required)
    title: str = Field(..., min_length=1, max_length=500)
    url: HttpUrl
    source_type: str  # "reddit", "hackernews", "devto", etc.
    external_id: str  # ID on the source platform

    # Content (optional - some sources only have title/link)
    content: Optional[str] = Field(None, max_length=50000)
    author: Optional[str] = Field(None, max_length=200)

    # Metadata
    published_at: datetime
    tags: List[str] = Field(default_factory=list)
    upvotes: int = 0
    comments_count: int = 0

    # Source-specific data (stored as JSON in DB)
    raw_data: dict = Field(default_factory=dict)

    @field_validator('tags')
    @classmethod
    def limit_tags(cls, v: List[str]) -> List[str]:
        """Limit to 10 tags maximum"""
        return v[:10] if v else []

    @field_validator('source_type')
    @classmethod
    def validate_source_type(cls, v: str) -> str:
        """Ensure source_type is lowercase"""
        return v.lower()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "FastAPI Best Practices 2024",
                "url": "https://example.com/article",
                "source_type": "reddit",
                "external_id": "abc123",
                "content": "Article content here...",
                "author": "john_doe",
                "published_at": "2024-01-15T10:30:00Z",
                "tags": ["python", "fastapi"],
                "upvotes": 142,
                "comments_count": 23,
                "raw_data": {}
            }
        }


class ScrapedYouTubeVideo(ScrapedArticle):
    """
    YouTube video extension of ScrapedArticle.

    Adds YouTube-specific fields for video metadata including channel information,
    thumbnail, duration, and view count.
    """

    video_id: str = Field(..., description="YouTube video ID (e.g., 'dQw4w9WgXcQ')")
    channel_id: str = Field(..., description="YouTube channel ID (e.g., 'UC_x5XG1OV2P6uZZ5FSM9Ttw')")
    channel_name: str = Field(..., description="Channel display name")
    thumbnail_url: Optional[HttpUrl] = Field(None, description="Video thumbnail URL")
    duration_seconds: Optional[int] = Field(None, ge=0, description="Video duration in seconds")
    view_count: Optional[int] = Field(None, ge=0, description="View count at scrape time")

    @field_validator('video_id', 'channel_id', 'channel_name')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Building a REST API with FastAPI",
                "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
                "source_type": "youtube_rss",
                "external_id": "dQw4w9WgXcQ",
                "author": "Tech Channel",
                "published_at": "2024-01-15T10:30:00",
                "video_id": "dQw4w9WgXcQ",
                "channel_id": "UC_x5XG1OV2P6uZZ5FSM9Ttw",
                "channel_name": "Tech Channel",
                "thumbnail_url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
                "duration_seconds": 1200,
                "view_count": 50000
            }
        }
