"""Tests for YouTube Trending Celery task"""
import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from app.tasks.scraping import scrape_youtube_trending_async
from app.models.scraping_run import ScrapingRun


@pytest.mark.asyncio
async def test_scrape_youtube_trending_async_success(db_session):
    """Test successful YouTube trending scraping task"""

    # Create test keywords
    from app.models.keyword import Keyword
    keywords = [
        Keyword(keyword="python", weight=5.0, category="programming", is_active=True),
        Keyword(keyword="rust", weight=4.0, category="programming", is_active=True),
    ]
    for kw in keywords:
        db_session.add(kw)
    db_session.commit()

    # Mock the scraper registry and scraper
    with patch('app.tasks.scraping.ScraperRegistry') as mock_registry_class:
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry

        # Create mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.scrape = AsyncMock(return_value=[
            Mock(
                video_id="vid1",
                title="Python Tutorial 2024",
                source_type="youtube_trending"
            ),
            Mock(
                video_id="vid2",
                title="Rust for Beginners",
                source_type="youtube_trending"
            )
        ])
        mock_registry.get.return_value = mock_scraper

        # Mock save_articles
        with patch('app.tasks.scraping.save_articles', new_callable=AsyncMock) as mock_save:
            mock_save.return_value = 2

            # Mock Redis
            with patch('app.tasks.scraping.redis.from_url', new_callable=AsyncMock) as mock_redis:
                mock_redis_client = AsyncMock()
                mock_redis.return_value = mock_redis_client

                # Run the task
                result = await scrape_youtube_trending_async(
                    db=db_session,
                    config={"region_code": "US", "max_results": 50},
                    task_id="test-yt-trending-123"
                )

                # Verify result
                assert result["status"] == "success"
                assert result["videos_scraped"] == 2
                assert result["videos_saved"] == 2
                assert result["keywords_used"] == 2

                # Verify scraper was called with correct keywords
                mock_scraper.scrape.assert_called_once()
                call_args = mock_scraper.scrape.call_args
                config_arg = call_args[0][0]
                keywords_arg = call_args[0][1]
                assert config_arg["region_code"] == "US"
                assert len(keywords_arg) == 2

                # Verify scraping run was logged
                run = db_session.query(ScrapingRun).filter_by(
                    task_id="test-yt-trending-123"
                ).first()
                assert run is not None
                assert run.status == "success"
                assert run.source_type == "youtube_trending"
                assert run.articles_scraped == 2


@pytest.mark.asyncio
async def test_scrape_youtube_trending_async_no_keywords(db_session):
    """Test task skips when no active keywords exist"""

    # No keywords in database

    result = await scrape_youtube_trending_async(
        db=db_session,
        config=None,
        task_id="test-no-keywords"
    )

    # Should skip
    assert result["status"] == "skipped"
    assert result["reason"] == "No active keywords"

    # Verify scraping run was logged as skipped
    run = db_session.query(ScrapingRun).filter_by(
        task_id="test-no-keywords"
    ).first()
    assert run is not None
    assert run.status == "skipped"


@pytest.mark.asyncio
async def test_scrape_youtube_trending_async_scraper_not_found(db_session):
    """Test task fails gracefully when scraper not in registry"""

    # Create test keyword
    from app.models.keyword import Keyword
    kw = Keyword(keyword="python", weight=5.0, category="programming", is_active=True)
    db_session.add(kw)
    db_session.commit()

    with patch('app.tasks.scraping.ScraperRegistry') as mock_registry_class:
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry
        mock_registry.get.return_value = None  # Scraper not found

        with patch('app.tasks.scraping.redis.from_url', new_callable=AsyncMock):
            result = await scrape_youtube_trending_async(
                db=db_session,
                config=None,
                task_id="test-no-scraper"
            )

            assert result["status"] == "error"
            assert "not found" in result["error"]


@pytest.mark.asyncio
async def test_scrape_youtube_trending_async_handles_error(db_session):
    """Test task handles scraper errors gracefully"""

    # Create test keyword
    from app.models.keyword import Keyword
    kw = Keyword(keyword="python", weight=5.0, category="programming", is_active=True)
    db_session.add(kw)
    db_session.commit()

    with patch('app.tasks.scraping.ScraperRegistry') as mock_registry_class:
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry

        # Mock scraper that fails
        mock_scraper = AsyncMock()
        mock_scraper.scrape = AsyncMock(side_effect=Exception("API quota exceeded"))
        mock_registry.get.return_value = mock_scraper

        with patch('app.tasks.scraping.redis.from_url', new_callable=AsyncMock):
            result = await scrape_youtube_trending_async(
                db=db_session,
                config=None,
                task_id="test-error"
            )

            assert result["status"] == "error"
            assert "API quota exceeded" in result["error"]

            # Verify scraping run was logged as failed
            run = db_session.query(ScrapingRun).filter_by(
                task_id="test-error"
            ).first()
            assert run.status == "failed"


def test_celery_task_registered():
    """Test that the Celery task is properly registered"""
    from app.tasks.celery_app import celery_app

    # Check task is registered
    assert 'scrape_youtube_trending' in celery_app.tasks

    # Check beat schedule includes the task
    assert 'scrape-youtube-trending-every-6-hours' in celery_app.conf.beat_schedule
    schedule_entry = celery_app.conf.beat_schedule['scrape-youtube-trending-every-6-hours']
    assert schedule_entry['task'] == 'scrape_youtube_trending'
