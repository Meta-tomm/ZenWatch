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
