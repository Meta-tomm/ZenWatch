import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.scrapers.plugins.youtube_trending import YouTubeTrendingScraper
from app.scrapers.registry import ScraperRegistry

def test_youtube_trending_registered():
    """Test scraper is registered"""
    registry = ScraperRegistry()
    scraper = registry.get('youtube_trending')

    assert scraper is not None
    assert isinstance(scraper, YouTubeTrendingScraper)

@pytest.mark.asyncio
async def test_youtube_trending_checks_quota():
    """Test scraper checks quota before scraping"""
    scraper = YouTubeTrendingScraper()

    # Mock quota manager to return False
    scraper.quota_manager = Mock()
    scraper.quota_manager.check_quota = AsyncMock(return_value=False)

    result = await scraper.scrape({}, [])

    # Should return empty list when quota exhausted
    assert result == []
    scraper.quota_manager.check_quota.assert_called_once()
