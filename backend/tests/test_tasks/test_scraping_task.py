import pytest
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
from app.tasks.scraping import scrape_all_sources_async
from app.models.scraping_run import ScrapingRun


@pytest.mark.asyncio
async def test_scrape_all_sources_success(db_session):
    """Test successful scraping from all active sources"""

    # Mock the registry and scrapers
    with patch('app.tasks.scraping.ScraperRegistry') as mock_registry_class:
        # Setup mock registry
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry

        # Mock HN scraper
        mock_hn_scraper = AsyncMock()
        mock_hn_scraper.validate_config = Mock(return_value=True)
        mock_hn_scraper.scrape.return_value = [
            {
                'title': 'Test HN Article',
                'url': 'https://news.ycombinator.com/item?id=123',
                'published_at': datetime(2024, 1, 1),
            }
        ]

        # Mock Reddit scraper
        mock_reddit_scraper = AsyncMock()
        mock_reddit_scraper.validate_config = Mock(return_value=True)
        mock_reddit_scraper.scrape.return_value = [
            {
                'title': 'Test Reddit Post',
                'url': 'https://reddit.com/r/python/123',
                'published_at': datetime(2024, 1, 1),
            }
        ]

        # Setup registry to return mock scrapers
        def get_scraper_side_effect(source_type):
            if source_type == 'hackernews':
                return mock_hn_scraper
            elif source_type == 'reddit':
                return mock_reddit_scraper
            return None

        mock_registry.get_scraper.side_effect = get_scraper_side_effect

        # Create test sources
        from app.models.source import Source
        hn_source = Source(
            name="HackerNews",
            type="hackernews",
            config={"max_articles": 10},
            is_active=True
        )
        reddit_source = Source(
            name="Reddit",
            type="reddit",
            config={
                "client_id": "test_id",
                "client_secret": "test_secret",
                "subreddits": ["python"]
            },
            is_active=True
        )

        db_session.add(hn_source)
        db_session.add(reddit_source)
        db_session.commit()

        # Run the task
        result = await scrape_all_sources_async(
            db=db_session,
            keywords=["python", "AI"],
            task_id="test-task-123"
        )

        # Verify results
        assert result['status'] == 'success'
        assert result['sources_scraped'] == 2
        assert result['total_articles'] >= 2


@pytest.mark.asyncio
async def test_scrape_all_sources_handles_errors(db_session):
    """Test that scraping continues even if one source fails"""

    with patch('app.tasks.scraping.ScraperRegistry') as mock_registry_class:
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry

        # Mock scraper that succeeds
        mock_success_scraper = AsyncMock()
        mock_success_scraper.validate_config = Mock(return_value=True)
        mock_success_scraper.scrape.return_value = [
            {'title': 'Article', 'url': 'https://example.com/1', 'published_at': datetime(2024, 1, 1)}
        ]

        # Mock scraper that fails
        mock_fail_scraper = AsyncMock()
        mock_fail_scraper.validate_config = Mock(return_value=True)
        mock_fail_scraper.scrape.side_effect = Exception("API error")

        def get_scraper_side_effect(source_type):
            if source_type == 'hackernews':
                return mock_success_scraper
            elif source_type == 'reddit':
                return mock_fail_scraper
            return None

        mock_registry.get_scraper.side_effect = get_scraper_side_effect

        from app.models.source import Source
        hn_source = Source(name="HN", type="hackernews", config={}, is_active=True)
        reddit_source = Source(name="Reddit", type="reddit", config={}, is_active=True)

        db_session.add(hn_source)
        db_session.add(reddit_source)
        db_session.commit()

        result = await scrape_all_sources_async(
            db=db_session,
            keywords=["python"],
            task_id="test-error-123"
        )

        # Should still succeed for working source
        assert result['status'] == 'partial_success'
        assert result['sources_scraped'] == 1
        assert result['errors'] == 1


@pytest.mark.asyncio
async def test_scrape_all_sources_logs_to_scraping_runs(db_session):
    """Test that scraping runs are logged to database"""

    with patch('app.tasks.scraping.ScraperRegistry') as mock_registry_class:
        mock_registry = Mock()
        mock_registry_class.return_value = mock_registry

        mock_scraper = AsyncMock()
        mock_scraper.validate_config = Mock(return_value=True)
        mock_scraper.scrape.return_value = [
            {'title': 'Article', 'url': 'https://example.com/1', 'published_at': datetime(2024, 1, 1)}
        ]

        mock_registry.get_scraper.return_value = mock_scraper

        from app.models.source import Source
        source = Source(name="HN", type="hackernews", config={}, is_active=True)
        db_session.add(source)
        db_session.commit()

        await scrape_all_sources_async(
            db=db_session,
            keywords=["python"],
            task_id='test-task-id-123'
        )

        # Check that scraping run was created
        run = db_session.query(ScrapingRun).filter_by(
            task_id='test-task-id-123'
        ).first()

        assert run is not None
        assert run.status == 'success'
        assert run.articles_scraped >= 1
