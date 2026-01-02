"""
Celery tasks for trend detection
"""

from datetime import datetime, timedelta, date
from sqlalchemy import func
from app.tasks.celery_app import celery_app
from app.database import SessionLocal
from app.models import Article, Keyword, Trend
from app.utils.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(name="detect_trends")
def detect_trends():
    """
    Détecte les tendances en analysant les articles récents

    Calcule un trend_score basé sur:
    - Fréquence du keyword dans les articles récents
    - Évolution par rapport aux jours précédents
    - Score moyen des articles contenant le keyword

    Returns:
        Dict avec statistiques
    """
    db = SessionLocal()

    try:
        # Analyse des 7 derniers jours
        days_to_analyze = 7
        today = date.today()
        start_date = today - timedelta(days=days_to_analyze)

        # Fetch active keywords
        keywords = db.query(Keyword).filter(Keyword.is_active == True).all()

        if not keywords:
            logger.warning("No active keywords - skipping trend detection")
            return {"status": "skipped", "reason": "no_keywords"}

        trends_created = 0

        for keyword in keywords:
            try:
                # Count articles containing this keyword in last 7 days
                articles_with_kw = db.query(Article).filter(
                    Article.published_at >= start_date,
                    func.lower(Article.title).contains(keyword.keyword.lower())
                ).all()

                article_count = len(articles_with_kw)

                if article_count == 0:
                    continue

                # Calculate average score for articles with this keyword
                avg_score = sum(a.score or 0 for a in articles_with_kw) / article_count

                # Calculate trend score
                # Simple formula: (article_count * keyword_weight * avg_score) / 10
                trend_score = (article_count * keyword.weight * avg_score) / 10

                # Check if trend already exists for today
                existing_trend = db.query(Trend).filter(
                    Trend.keyword == keyword.keyword,
                    Trend.date == today
                ).first()

                if existing_trend:
                    # Update existing
                    existing_trend.trend_score = trend_score
                    existing_trend.article_count = article_count
                    existing_trend.category = keyword.category
                else:
                    # Create new trend
                    new_trend = Trend(
                        keyword=keyword.keyword,
                        category=keyword.category,
                        trend_score=trend_score,
                        article_count=article_count,
                        date=today
                    )
                    db.add(new_trend)
                    trends_created += 1

                logger.debug(f"Trend for '{keyword.keyword}': score={trend_score:.2f}, articles={article_count}")

            except Exception as e:
                logger.error(f"Error detecting trend for keyword {keyword.keyword}: {e}")
                continue

        db.commit()
        logger.info(f"Trend detection complete: {trends_created} new trends created")

        return {
            "status": "success",
            "trends_created": trends_created,
            "keywords_analyzed": len(keywords)
        }

    except Exception as e:
        logger.error(f"Error in detect_trends task: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        db.close()


@celery_app.task(name="cleanup_old_trends")
def cleanup_old_trends(days_to_keep: int = 90):
    """
    Nettoie les anciennes tendances

    Args:
        days_to_keep: Nombre de jours de tendances à conserver (défaut: 90)

    Returns:
        Dict avec statistiques
    """
    db = SessionLocal()

    try:
        cutoff_date = date.today() - timedelta(days=days_to_keep)

        # Delete old trends
        deleted_count = db.query(Trend).filter(Trend.date < cutoff_date).delete()

        db.commit()
        logger.info(f"Cleaned up {deleted_count} old trends (older than {cutoff_date})")

        return {
            "status": "success",
            "trends_deleted": deleted_count,
            "cutoff_date": str(cutoff_date)
        }

    except Exception as e:
        logger.error(f"Error in cleanup_old_trends task: {e}")
        db.rollback()
        return {"status": "error", "error": str(e)}

    finally:
        db.close()
