from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.tasks.celery_app import celery_app
from app.database import get_db
from app.models.source import Source
from app.models.scraping_run import ScrapingRun
from app.scrapers.registry import ScraperRegistry
from app.scrapers.storage import save_articles
from app.utils.logger import get_logger

# Import scrapers to trigger plugin registration
import app.scrapers

logger = get_logger(__name__)


async def scrape_all_sources_async(
    db: Session,
    keywords: List[str] = None,
    task_id: Optional[str] = None
) -> Dict:
    """
    Scrape all active sources and save articles to database (async business logic)

    Args:
        db: Database session
        keywords: List of keywords to filter articles (optional)
        task_id: Task ID for tracking (optional)

    Returns:
        Dictionary with scraping results and statistics

    This function:
    1. Fetches all active sources from database
    2. For each source, gets the appropriate scraper from registry
    3. Runs scraper with configured keywords
    4. Saves articles to database with deduplication
    5. Logs results to scraping_runs table
    """
    # Use default keywords if none provided
    if keywords is None:
        keywords = ["python", "AI", "machine learning", "blockchain"]

    logger.info(f"Starting scraping task {task_id} with keywords: {keywords}")

    # Create scraping run record
    scraping_run = ScrapingRun(
        task_id=task_id or "manual",
        source_type="all",
        status="running",
        articles_scraped=0,
        articles_saved=0
    )
    db.add(scraping_run)
    db.commit()

    registry = ScraperRegistry()
    total_articles = 0
    sources_scraped = 0
    errors_count = 0
    results = []

    try:
        # Get all active sources
        active_sources = db.query(Source).filter_by(is_active=True).all()
        logger.info(f"Found {len(active_sources)} active sources")

        for source in active_sources:
            try:
                logger.info(f"Scraping source: {source.name} ({source.type})")

                # Get scraper from registry
                scraper = registry.get(source.type)
                if not scraper:
                    logger.warning(f"No scraper found for source type: {source.type}")
                    continue

                # Validate config
                if not scraper.validate_config(source.config):
                    logger.error(f"Invalid config for source {source.name}")
                    continue

                # Scrape articles (async with context manager for HTTP client)
                async with scraper:
                    articles = await scraper.scrape(source.config, keywords)

                logger.info(f"Scraped {len(articles)} articles from {source.name}")

                # Save articles to database
                if articles:
                    saved_count = await save_articles(articles, source.type, db)
                    total_articles += saved_count
                    logger.info(f"Saved {saved_count} articles from {source.name}")

                sources_scraped += 1

                # Update source last_scraped_at
                source.last_scraped_at = datetime.utcnow()
                db.commit()

                results.append({
                    'source': source.name,
                    'status': 'success',
                    'articles': len(articles),
                    'saved': saved_count if articles else 0
                })

            except Exception as e:
                logger.error(f"Error scraping {source.name}: {str(e)}", exc_info=True)
                errors_count += 1
                results.append({
                    'source': source.name,
                    'status': 'error',
                    'error': str(e)
                })
                continue

        # Determine overall status
        if errors_count == 0:
            status = 'success'
        elif sources_scraped > 0:
            status = 'partial_success'
        else:
            status = 'failed'

        # Update scraping run
        scraping_run.status = status
        scraping_run.articles_scraped = total_articles
        scraping_run.articles_saved = total_articles
        scraping_run.completed_at = datetime.utcnow()

        if errors_count > 0:
            scraping_run.error_message = f"{errors_count} source(s) failed"

        db.commit()

        logger.info(
            f"Scraping task {task_id} completed: "
            f"{sources_scraped} sources, {total_articles} articles, "
            f"{errors_count} errors"
        )

        return {
            'task_id': task_id,
            'status': status,
            'sources_scraped': sources_scraped,
            'total_articles': total_articles,
            'errors': errors_count,
            'results': results
        }

    except Exception as e:
        logger.error(f"Fatal error in scraping task {task_id}: {str(e)}", exc_info=True)

        # Update scraping run as failed
        scraping_run.status = 'failed'
        scraping_run.error_message = str(e)
        scraping_run.completed_at = datetime.utcnow()
        db.commit()

        raise


@celery_app.task(bind=True, name='scrape_all_sources')
def scrape_all_sources(self, keywords: List[str] = None) -> Dict:
    """
    Celery task wrapper for scraping all sources

    Args:
        keywords: List of keywords to filter articles

    Returns:
        Dictionary with scraping results
    """
    import asyncio

    # Get database session
    db = next(get_db())

    try:
        # Run the async function
        result = asyncio.run(
            scrape_all_sources_async(
                db=db,
                keywords=keywords,
                task_id=self.request.id
            )
        )
        return result
    finally:
        db.close()
