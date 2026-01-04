import pytest
from unittest.mock import Mock, patch
from app.scrapers.plugins.youtube_rss import YouTubeRSSScraper
from app.scrapers.registry import ScraperRegistry

def test_youtube_rss_scraper_registered():
    """Test scraper is registered in registry"""
    registry = ScraperRegistry()
    scraper = registry.get('youtube_rss')

    assert scraper is not None
    assert isinstance(scraper, YouTubeRSSScraper)

@pytest.mark.asyncio
async def test_youtube_rss_scraper_config_validation():
    """Test config validation"""
    scraper = YouTubeRSSScraper()

    # Should accept any config (fetches from DB)
    assert scraper.validate_config({}) == True
    assert scraper.validate_config({'channel_id': 'test'}) == True
