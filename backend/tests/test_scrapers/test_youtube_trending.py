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


def test_parse_iso8601_duration():
    """Test parsing ISO 8601 duration to seconds"""
    scraper = YouTubeTrendingScraper()

    # Test various duration formats
    assert scraper._parse_duration("PT4M13S") == 253
    assert scraper._parse_duration("PT1H2M3S") == 3723
    assert scraper._parse_duration("PT30S") == 30
    assert scraper._parse_duration("PT5M") == 300
    assert scraper._parse_duration("PT1H") == 3600


def test_parse_iso8601_duration_invalid():
    """Test invalid duration returns None"""
    scraper = YouTubeTrendingScraper()

    assert scraper._parse_duration("invalid") is None
    assert scraper._parse_duration("") is None
    assert scraper._parse_duration(None) is None
