from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, date
from app.database import get_db
from app.models import Article, Keyword, Source, Trend
from app.schemas.analytics import (
    AnalyticsSummaryResponse,
    DailyStatsResponse,
    CategoryStatsResponse,
    TrendResponse,
    WeeklyTrendResponse
)
from app.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Résumé global des analytics

    - Total articles, sources, keywords
    - Score moyen derniers 7 jours
    - Top tendances
    - Répartition par catégorie
    """
    # Total counts
    total_articles = db.query(func.count(Article.id)).scalar()
    total_sources = db.query(func.count(Source.id)).filter(Source.is_active == True).scalar()
    total_keywords = db.query(func.count(Keyword.id)).filter(Keyword.is_active == True).scalar()

    # Avg score last 7 days
    seven_days_ago = datetime.now() - timedelta(days=7)
    avg_score = db.query(func.avg(Article.score)).filter(
        Article.scraped_at >= seven_days_ago,
        Article.score.isnot(None)
    ).scalar() or 0.0

    # Articles scraped today
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    articles_today = db.query(func.count(Article.id)).filter(
        Article.scraped_at >= today_start
    ).scalar()

    # Top trends (last 7 days)
    top_trends_query = db.query(Trend).filter(
        Trend.date >= (date.today() - timedelta(days=7))
    ).order_by(desc(Trend.trend_score)).limit(10).all()

    # Articles by category
    categories = db.query(
        Article.category,
        func.count(Article.id)
    ).filter(
        Article.category.isnot(None)
    ).group_by(Article.category).all()

    articles_by_category = {cat: count for cat, count in categories}

    return AnalyticsSummaryResponse(
        total_articles=total_articles,
        total_sources=total_sources,
        total_keywords=total_keywords,
        avg_score_last_7_days=round(avg_score, 2),
        top_trends=top_trends_query,
        articles_by_category=articles_by_category,
        articles_scraped_today=articles_today
    )


@router.get("/analytics/daily-stats")
async def get_daily_stats(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Statistiques quotidiennes

    - **days**: Nombre de jours à récupérer (1-90)
    """
    start_date = datetime.now() - timedelta(days=days)

    # Query avec agrégation par jour et catégorie
    stats = db.query(
        func.date(Article.published_at).label('date'),
        Article.category,
        func.count(Article.id).label('article_count'),
        func.avg(Article.score).label('avg_score'),
        func.sum(func.cast(Article.is_read, db.Integer)).label('read_count'),
        func.sum(func.cast(Article.is_favorite, db.Integer)).label('favorite_count')
    ).filter(
        Article.published_at >= start_date,
        Article.category.isnot(None)
    ).group_by(
        func.date(Article.published_at),
        Article.category
    ).all()

    # Restructure data
    daily_data = {}
    for stat in stats:
        date_key = stat.date
        if date_key not in daily_data:
            daily_data[date_key] = {
                "date": date_key,
                "total_articles": 0,
                "categories": []
            }

        daily_data[date_key]["total_articles"] += stat.article_count
        daily_data[date_key]["categories"].append(
            CategoryStatsResponse(
                category=stat.category,
                article_count=stat.article_count,
                avg_score=round(stat.avg_score or 0.0, 2),
                read_count=stat.read_count or 0,
                favorite_count=stat.favorite_count or 0
            )
        )

    result = [
        DailyStatsResponse(
            date=data["date"],
            total_articles=data["total_articles"],
            avg_score=round(
                sum(c.avg_score * c.article_count for c in data["categories"]) / data["total_articles"],
                2
            ) if data["total_articles"] > 0 else 0.0,
            categories=data["categories"]
        )
        for data in daily_data.values()
    ]

    # Sort by date descending
    result.sort(key=lambda x: x.date, reverse=True)

    logger.info(f"Retrieved daily stats for {len(result)} days")
    return result


@router.get("/analytics/trends", response_model=list[TrendResponse])
async def get_trends(
    days: int = Query(7, ge=1, le=90),
    category: str = Query(None),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Récupère les tendances détectées

    - **days**: Période en jours (1-90)
    - **category**: Filtrer par catégorie
    - **limit**: Nombre max de résultats
    """
    start_date = date.today() - timedelta(days=days)

    query = db.query(Trend).filter(Trend.date >= start_date)

    if category:
        query = query.filter(Trend.category == category)

    trends = query.order_by(desc(Trend.trend_score)).limit(limit).all()

    logger.info(f"Retrieved {len(trends)} trends (last {days} days)")
    return trends


@router.get("/analytics/weekly-trends", response_model=list[WeeklyTrendResponse])
async def get_weekly_trends(
    weeks: int = Query(4, ge=1, le=52),
    db: Session = Depends(get_db)
):
    """
    Tendances hebdomadaires agrégées

    - **weeks**: Nombre de semaines à récupérer (1-52)
    """
    start_date = date.today() - timedelta(weeks=weeks * 7)

    # Query from vw_weekly_trends view
    result = db.execute(f"""
        SELECT
            week_start,
            keyword,
            category,
            avg_trend_score,
            total_articles
        FROM vw_weekly_trends
        WHERE week_start >= '{start_date}'
        ORDER BY week_start DESC, avg_trend_score DESC
        LIMIT 50
    """)

    trends = [
        WeeklyTrendResponse(
            week_start=row[0],
            keyword=row[1],
            category=row[2],
            avg_trend_score=round(row[3] or 0.0, 2),
            total_articles=row[4] or 0
        )
        for row in result
    ]

    logger.info(f"Retrieved {len(trends)} weekly trends")
    return trends


@router.get("/analytics/top-keywords")
async def get_top_keywords(
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Top keywords par fréquence dans les tendances

    - **days**: Période en jours
    - **limit**: Nombre de keywords à retourner
    """
    start_date = date.today() - timedelta(days=days)

    top_keywords = db.query(
        Trend.keyword,
        Trend.category,
        func.sum(Trend.article_count).label('total_articles'),
        func.avg(Trend.trend_score).label('avg_score')
    ).filter(
        Trend.date >= start_date
    ).group_by(
        Trend.keyword,
        Trend.category
    ).order_by(
        desc('total_articles')
    ).limit(limit).all()

    result = [
        {
            "keyword": kw.keyword,
            "category": kw.category,
            "total_articles": kw.total_articles,
            "avg_score": round(kw.avg_score or 0.0, 2)
        }
        for kw in top_keywords
    ]

    return {"top_keywords": result}
