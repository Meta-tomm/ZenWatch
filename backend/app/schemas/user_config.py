from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import time, datetime


class UserConfigBase(BaseModel):
    """Base schema pour UserConfig"""
    email: EmailStr
    daily_digest_enabled: bool = True
    digest_time: time = Field(default=time(8, 0))  # 08:00 par défaut
    min_score_threshold: float = Field(default=50.0, ge=0.0, le=100.0)
    preferred_categories: Optional[list[str]] = None
    email_frequency: str = Field(default="daily", pattern="^(daily|weekly)$")


class UserConfigCreate(UserConfigBase):
    """Schema pour créer une config utilisateur"""
    pass


class UserConfigUpdate(BaseModel):
    """Schema pour mettre à jour une config utilisateur"""
    email: Optional[EmailStr] = None
    daily_digest_enabled: Optional[bool] = None
    digest_time: Optional[time] = None
    min_score_threshold: Optional[float] = Field(None, ge=0.0, le=100.0)
    preferred_categories: Optional[list[str]] = None
    email_frequency: Optional[str] = Field(None, pattern="^(daily|weekly)$")


class UserConfigResponse(UserConfigBase):
    """Schema de réponse pour une config utilisateur"""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
