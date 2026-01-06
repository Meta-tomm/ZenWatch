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
            else:
                article_data = article.copy()

            # Convert HttpUrl objects to strings
            for key in ['url', 'thumbnail_url']:
                if key in article_data and article_data[key] is not None:
                    article_data[key] = str(article_data[key])

            # Remove source_type and set source_id instead
            original_source_type = article_data.pop('source_type', None)
            article_data['source_id'] = source.id

            # Set is_video based on source_type
            if source_type in ('youtube_rss', 'youtube_trending', 'youtube'):
                article_data['is_video'] = True

            # Check if article already exists by URL
            existing = db.query(Article).filter_by(url=article_data['url']).first()

            # Filter to only include valid Article fields
            valid_fields = {c.name for c in Article.__table__.columns}
            filtered_data = {k: v for k, v in article_data.items() if k in valid_fields}

            if existing:
                # Update existing article
                for key, value in filtered_data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)

                logger.debug(f"Updated article: {filtered_data['url']}")
            else:
                # Create new article
                article = Article(**filtered_data)
                db.add(article)
                logger.debug(f"Created new article: {filtered_data['url']}")

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
