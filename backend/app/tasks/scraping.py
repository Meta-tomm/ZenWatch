from typing import List, Dict, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session
import redis.asyncio as redis
from app.tasks.celery_app import celery_app
from app.database import get_db
from app.models.source import Source
from app.models.keyword import Keyword
from app.models.scraping_run import ScrapingRun
from app.scrapers.registry import ScraperRegistry
from app.scrapers.storage import save_articles
from app.utils.logger import get_logger
from app.config import settings

# Import scrapers to trigger plugin registration
import app.scrapers

logger = get_logger(__name__)


# YouTube Trending Scraper Task
async def scrape_youtube_trending_async(
    db: Session,
    config: Dict[str, Any] = None,
    task_id: Optional[str] = None
) -> Dict:
    """
    Scrape trending YouTube videos filtered by active keywords.

    Args:
        db: Database session
        config: Scraper config (region_code, max_results, video_category)
        task_id: Task ID for tracking

    Returns:
        Dictionary with scraping results
    """
    # Default config
    if config is None:
        config = {
            "region_code": "US",
            "max_results": 50,
            "video_category": "28",  # Science & Technology
            "min_keyword_matches": 1,
            "include_shorts": True,
            "min_view_count": 0
        }

    logger.info(f"Starting YouTube Trending scraping task {task_id}")

    # Create scraping run record
    scraping_run = ScrapingRun(
        task_id=task_id or "manual-yt-trending",
        source_type="youtube_trending",
        status="running",
        articles_scraped=0,
        articles_saved=0
    )
    db.add(scraping_run)
    db.commit()

    # Initialize Redis client for quota management
    redis_client = None
    try:
        redis_client = await redis.from_url(settings.REDIS_URL)
        logger.info("Redis client initialized for YouTube quota management")
    except Exception as e:
        logger.warning(f"Failed to initialize Redis: {e}. Quota tracking disabled.")

    try:
        # Get active keywords from database
        active_keywords = db.query(Keyword).filter_by(is_active=True).all()
        if not active_keywords:
            logger.warning("No active keywords found, returning empty results")
            scraping_run.status = "skipped"
            scraping_run.error_message = "No active keywords"
            scraping_run.completed_at = datetime.utcnow()
            db.commit()
            return {
                "task_id": task_id,
                "status": "skipped",
                "reason": "No active keywords"
            }

        # Prepare keywords for scraper (list of dicts with keyword, weight, category)
        keyword_data = [
            {
                "keyword": kw.keyword,
                "weight": kw.weight,
                "category": kw.category
            }
            for kw in active_keywords
        ]
        logger.info(f"Using {len(keyword_data)} active keywords")

        # Get YouTube Trending scraper from registry
        registry = ScraperRegistry()
        scraper = registry.get("youtube_trending")

        if not scraper:
            logger.error("YouTube Trending scraper not found in registry")
            scraping_run.status = "failed"
            scraping_run.error_message = "Scraper not found"
            scraping_run.completed_at = datetime.utcnow()
            db.commit()
            return {
                "task_id": task_id,
                "status": "error",
                "error": "YouTube Trending scraper not found"
            }

        # Inject Redis client for quota management
        if redis_client:
            scraper.redis = redis_client

        # Run scraper
        videos = await scraper.scrape(config, keyword_data)
        scraped_count = len(videos)
        logger.info(f"Scraped {scraped_count} trending videos")

        # Save videos to database
        saved_count = 0
        if videos:
            saved_count = await save_articles(videos, "youtube_trending", db)
            logger.info(f"Saved {saved_count} videos ({scraped_count - saved_count} duplicates)")

        # Update scraping run
        scraping_run.status = "success"
        scraping_run.articles_scraped = scraped_count
        scraping_run.articles_saved = saved_count
        scraping_run.completed_at = datetime.utcnow()
        db.commit()

        return {
            "task_id": task_id,
            "status": "success",
            "videos_scraped": scraped_count,
            "videos_saved": saved_count,
            "duplicates": scraped_count - saved_count,
            "keywords_used": len(keyword_data)
        }

    except Exception as e:
        logger.error(f"YouTube Trending scraping failed: {e}", exc_info=True)
        scraping_run.status = "failed"
        scraping_run.error_message = str(e)
        scraping_run.completed_at = datetime.utcnow()
        db.commit()
        return {
            "task_id": task_id,
            "status": "error",
            "error": str(e)
        }

    finally:
        if redis_client:
            try:
                await redis_client.aclose()
            except Exception as e:
                logger.warning(f"Error closing Redis client: {e}")


@celery_app.task(bind=True, name='scrape_youtube_trending')
def scrape_youtube_trending(self, config: Dict[str, Any] = None, run_scoring: bool = True) -> Dict:
    """
    Celery task: Scrape trending YouTube videos.
    Runs every 6 hours by default.

    Args:
        config: Optional scraper configuration
        run_scoring: Whether to run scoring after scraping (default: True)

    Returns:
        Dictionary with scraping results

    Example:
        # Trigger manually
        result = scrape_youtube_trending.delay()

        # With custom config
        result = scrape_youtube_trending.delay({'region_code': 'GB', 'max_results': 25})
    """
    import asyncio
    from app.tasks.scoring import score_articles

    db = next(get_db())
    try:
        result = asyncio.run(
            scrape_youtube_trending_async(
                db=db,
                config=config,
                task_id=self.request.id
            )
        )

        # Chain scoring task if scraping was successful
        if run_scoring and result.get('videos_saved', 0) > 0:
            logger.info(f"Chaining score_articles task after YouTube trending ({result['videos_saved']} new videos)")
            score_articles.delay()

        return result
    finally:
        db.close()


async def scrape_all_sources_async(
    db: Session,
    keywords: List[str] = None,
    task_id: Optional[str] = None
) -> Dict:
    """
    Scrape all active sources and save articles to database (async business logic)

    Args:
        db: Database session
        keywords: List of keywords to filter articles (optional, fetched from DB if None)
        task_id: Task ID for tracking (optional)

    Returns:
        Dictionary with scraping results and statistics

    This function:
    1. Fetches active keywords from database (if not provided)
    2. Fetches all active sources from database
    3. For each source, gets the appropriate scraper from registry
    4. Runs scraper with Redis caching enabled
    5. Saves articles to database with deduplication
    6. Logs results to scraping_runs table
    """
    # Get keywords from database if not provided
    if keywords is None:
        active_keywords = db.query(Keyword).filter_by(is_active=True).all()
        if active_keywords:
            keywords = [kw.keyword for kw in active_keywords]
            logger.info(f"Using {len(keywords)} active keywords from database")
        else:
            # Fallback to default keywords
            keywords = ["python", "AI", "rust", "javascript", "kubernetes"]
            logger.warning(f"No active keywords found, using defaults: {keywords}")

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
    total_articles_scraped = 0
    total_articles_saved = 0
    sources_scraped = 0
    errors_count = 0
    results = []

    # Initialize Redis client for caching
    redis_client = None
    try:
        redis_client = await redis.from_url(settings.REDIS_URL)
        logger.info("Redis client initialized for caching")
    except Exception as e:
        logger.warning(f"Failed to initialize Redis client: {e}. Caching disabled.")

    try:
        # Get all active sources
        active_sources = db.query(Source).filter_by(is_active=True).all()
        logger.info(f"Found {len(active_sources)} active sources")

        for source in active_sources:
            source_start_time = datetime.utcnow()

            try:
                logger.info(f"Scraping source: {source.name} ({source.type})")

                # Get scraper from registry
                scraper = registry.get(source.type)
                if not scraper:
                    logger.warning(f"No scraper found for source type: {source.type}")
                    errors_count += 1
                    results.append({
                        'source': source.name,
                        'status': 'error',
                        'error': 'Scraper not found'
                    })
                    continue

                # Inject Redis client for caching
                if redis_client:
                    scraper.redis = redis_client

                # Inject YouTube channels for youtube_rss scraper
                if source.type == 'youtube_rss':
                    from app.models.youtube_channel import YouTubeChannel
                    channels = db.query(YouTubeChannel).filter_by(is_active=True).all()
                    scraper._channels = channels
                    logger.info(f"Injected {len(channels)} YouTube channels")

                # Validate config
                if not scraper.validate_config(source.config):
                    logger.error(f"Invalid config for source {source.name}")
                    errors_count += 1
                    results.append({
                        'source': source.name,
                        'status': 'error',
                        'error': 'Invalid configuration'
                    })
                    continue

                # Scrape articles with caching
                async with scraper:
                    # Use scrape_with_cache to leverage Redis caching
                    articles = await scraper.scrape_with_cache(source.config, keywords)

                scraped_count = len(articles)
                total_articles_scraped += scraped_count
                logger.info(f"Scraped {scraped_count} articles from {source.name}")

                # Save articles to database
                saved_count = 0
                if articles:
                    saved_count = await save_articles(articles, source.type, db)
                    total_articles_saved += saved_count
                    logger.info(f"Saved {saved_count} articles from {source.name} ({scraped_count - saved_count} duplicates)")

                sources_scraped += 1

                # Update source last_scraped_at
                source.last_scraped_at = datetime.utcnow()
                db.commit()

                # Calculate duration
                duration_seconds = (datetime.utcnow() - source_start_time).total_seconds()

                results.append({
                    'source': source.name,
                    'status': 'success',
                    'articles_scraped': scraped_count,
                    'articles_saved': saved_count,
                    'duplicates': scraped_count - saved_count,
                    'duration_seconds': round(duration_seconds, 2)
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
        scraping_run.articles_scraped = total_articles_scraped
        scraping_run.articles_saved = total_articles_saved
        scraping_run.completed_at = datetime.utcnow()

        if errors_count > 0:
            scraping_run.error_message = f"{errors_count} source(s) failed"

        db.commit()

        logger.info(
            f"Scraping task {task_id} completed: "
            f"{sources_scraped}/{len(active_sources)} sources successful, "
            f"{total_articles_scraped} articles scraped, "
            f"{total_articles_saved} saved, "
            f"{total_articles_scraped - total_articles_saved} duplicates, "
            f"{errors_count} errors"
        )

        return {
            'task_id': task_id,
            'status': status,
            'sources_total': len(active_sources),
            'sources_scraped': sources_scraped,
            'articles_scraped': total_articles_scraped,
            'articles_saved': total_articles_saved,
            'duplicates': total_articles_scraped - total_articles_saved,
            'errors': errors_count,
            'keywords_used': keywords,
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

    finally:
        # Close Redis client
        if redis_client:
            try:
                await redis_client.aclose()
                logger.debug("Redis client closed")
            except Exception as e:
                logger.warning(f"Error closing Redis client: {e}")


@celery_app.task(bind=True, name='scrape_all_sources')
def scrape_all_sources(self, keywords: List[str] = None, run_scoring: bool = True) -> Dict:
    """
    Celery task wrapper for scraping all sources

    Args:
        keywords: List of keywords to filter articles (optional)
        run_scoring: Whether to run scoring after scraping (default: True)

    Returns:
        Dictionary with scraping results

    Example:
        # Trigger manually
        result = scrape_all_sources.delay()
        result = scrape_all_sources.delay(['python', 'rust'])

        # Or apply async
        task = scrape_all_sources.apply_async(kwargs={'keywords': ['AI', 'blockchain']})
    """
    import asyncio
    from app.tasks.scoring import score_articles

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

        # Chain scoring task if scraping was successful and articles were saved
        if run_scoring and result.get('articles_saved', 0) > 0:
            logger.info(f"Chaining score_articles task after scraping ({result['articles_saved']} new articles)")
            score_articles.delay()

        return result
    finally:
        db.close()
