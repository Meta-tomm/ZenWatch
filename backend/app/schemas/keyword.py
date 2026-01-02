from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class KeywordBase(BaseModel):
    """Base schema pour Keyword"""
    keyword: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    weight: float = Field(default=1.0, ge=1.0, le=5.0)
    is_active: bool = True


class KeywordCreate(KeywordBase):
    """Schema pour créer un nouveau keyword"""
    pass


class KeywordUpdate(BaseModel):
    """Schema pour mettre à jour un keyword"""
    keyword: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, max_length=100)
    weight: Optional[float] = Field(None, ge=1.0, le=5.0)
    is_active: Optional[bool] = None


class KeywordResponse(KeywordBase):
    """Schema de réponse pour un keyword"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KeywordListResponse(BaseModel):
    """Schema de réponse pour une liste de keywords"""
    keywords: list[KeywordResponse]
    total: int
