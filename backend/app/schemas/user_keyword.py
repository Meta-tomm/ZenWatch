from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class UserKeywordCreate(BaseModel):
    """Create a new user keyword."""
    keyword: str = Field(..., min_length=1, max_length=100)
    category: Optional[str] = Field(None, max_length=50)
    weight: float = Field(1.0, ge=0.1, le=5.0)


class UserKeywordUpdate(BaseModel):
    """Update an existing user keyword."""
    category: Optional[str] = Field(None, max_length=50)
    weight: Optional[float] = Field(None, ge=0.1, le=5.0)
    is_active: Optional[bool] = None


class UserKeywordResponse(BaseModel):
    """User keyword response."""
    id: int
    user_id: int
    keyword: str
    category: Optional[str] = None
    weight: float = 1.0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserKeywordList(BaseModel):
    """List of user keywords."""
    data: list[UserKeywordResponse]
    total: int
