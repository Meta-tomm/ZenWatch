from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class TrendResponse(BaseModel):
    """Schema de réponse pour une tendance"""
    id: int
    keyword: str
    category: Optional[str]
    trend_score: float
    article_count: int
    date: date
    created_at: datetime

    class Config:
        from_attributes = True


class CategoryStatsResponse(BaseModel):
    """Statistiques par catégorie"""
    category: str
    article_count: int
    avg_score: float
    read_count: int
    favorite_count: int


class DailyStatsResponse(BaseModel):
    """Statistiques quotidiennes"""
    date: date
    total_articles: int
    avg_score: float
    categories: list[CategoryStatsResponse]


class AnalyticsSummaryResponse(BaseModel):
    """Résumé global des analytics"""
    total_articles: int
    total_sources: int
    total_keywords: int
    avg_score_last_7_days: float
    top_trends: list[TrendResponse]
    articles_by_category: dict[str, int]
    articles_scraped_today: int


class WeeklyTrendResponse(BaseModel):
    """Tendances hebdomadaires"""
    week_start: date
    keyword: str
    category: Optional[str]
    avg_trend_score: float
    total_articles: int

    class Config:
        from_attributes = True
