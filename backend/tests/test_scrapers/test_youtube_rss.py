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

@pytest.mark.asyncio
async def test_parse_rss_entry():
    """Test parsing RSS entry to ScrapedYouTubeVideo"""
    scraper = YouTubeRSSScraper()

    # Mock RSS entry
    entry = Mock()
    entry.title = 'Test Video Title'
    entry.link = 'https://www.youtube.com/watch?v=test123'
    entry.yt_videoid = 'test123'
    entry.published_parsed = (2026, 1, 3, 12, 0, 0, 0, 0, 0)
    entry.get = Mock(return_value='Test video description')
    entry.media_thumbnail = [{'url': 'https://i.ytimg.com/vi/test123/hqdefault.jpg'}]

    channel = Mock()
    channel.channel_id = 'UC_test'
    channel.channel_name = 'Test Channel'

    video = scraper._parse_rss_entry(entry, channel)

    assert video.title == 'Test Video Title'
    assert video.video_id == 'test123'
    assert video.channel_id == 'UC_test'
    assert video.channel_name == 'Test Channel'
    assert video.source_type == 'youtube_rss'
