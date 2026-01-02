from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.article import Article
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def save_articles(
    articles: List[Dict],
    source_type: str,
    db: Session
) -> int:
    """
    Save articles to database with deduplication

    Args:
        articles: List of article dictionaries
        source_type: Type of source (reddit, hackernews, etc.)
        db: Database session

    Returns:
        Number of articles saved (new + updated)

    Logic:
        - Check if article URL already exists
        - If exists: update with new data
        - If new: insert
    """
    saved_count = 0

    for article_data in articles:
        try:
            # Ensure source_type is set (use provided one if not in data)
            if 'source_type' not in article_data:
                article_data['source_type'] = source_type

            # Check if article already exists by URL
            existing = db.query(Article).filter_by(url=article_data['url']).first()

            if existing:
                # Update existing article
                for key, value in article_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)

                logger.debug(f"Updated article: {article_data['url']}")
            else:
                # Create new article
                article = Article(**article_data)
                db.add(article)
                logger.debug(f"Created new article: {article_data['url']}")

            saved_count += 1

        except Exception as e:
            logger.error(f"Error saving article {article_data.get('url')}: {e}")
            continue

    # Commit all changes
    try:
        db.commit()
        logger.info(f"Saved {saved_count} articles from {source_type}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error committing articles: {e}")
        raise

    return saved_count
