from typing import List, Dict, Union
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.article import Article
from app.models.source import Source
from app.schemas.scraped_article import ScrapedArticle
from app.utils.logger import get_logger

logger = get_logger(__name__)


async def save_articles(
    articles: List[Union[Dict, ScrapedArticle]],
    source_type: str,
    db: Session
) -> int:
    """
    Save articles to database with deduplication

    Args:
        articles: List of article dictionaries or ScrapedArticle models
        source_type: Type of source (reddit, hackernews, etc.)
        db: Database session

    Returns:
        Number of articles saved (new + updated)

    Logic:
        - Check if article URL already exists
        - If exists: update with new data
        - If new: insert
    """
    # Get source_id from source_type
    source = db.query(Source).filter_by(type=source_type).first()
    if not source:
        logger.error(f"Source not found for type: {source_type}")
        return 0

    saved_count = 0

    for article in articles:
        try:
            # Convert ScrapedArticle to dict if needed
            if isinstance(article, ScrapedArticle):
                # mode='python' converts Pydantic types (HttpUrl, etc.) to native Python types
                article_data = article.model_dump(mode='python', exclude={'raw_data'})
                # Explicitly convert HttpUrl to str (Pydantic v2 doesn't always do this automatically)
                if 'url' in article_data:
                    article_data['url'] = str(article_data['url'])
            else:
                article_data = article.copy()

            # Remove source_type and set source_id instead
            article_data.pop('source_type', None)
            article_data['source_id'] = source.id

            # Check if article already exists by URL
            existing = db.query(Article).filter_by(url=article_data['url']).first()

            if existing:
                # Update existing article
                for key, value in article_data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)

                logger.debug(f"Updated article: {article_data['url']}")
            else:
                # Create new article
                article = Article(**article_data)
                db.add(article)
                logger.debug(f"Created new article: {article_data['url']}")

            saved_count += 1

        except Exception as e:
            url = article.url if isinstance(article, ScrapedArticle) else article.get('url', 'unknown')
            logger.error(f"Error saving article {url}: {e}")
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
