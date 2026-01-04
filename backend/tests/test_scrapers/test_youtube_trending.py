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


def test_parse_trending_video():
    """Test parsing YouTube API video response into ScrapedYouTubeVideo"""
    scraper = YouTubeTrendingScraper()

    # Mock YouTube API response structure
    video_data = {
        "id": "dQw4w9WgXcQ",
        "snippet": {
            "publishedAt": "2009-10-25T06:57:33Z",
            "channelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
            "title": "Rick Astley - Never Gonna Give You Up",
            "description": "The official video for Never Gonna Give You Up",
            "channelTitle": "Rick Astley",
            "tags": ["rick astley", "music", "80s"],
            "thumbnails": {
                "maxres": {"url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"},
                "high": {"url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg"},
                "medium": {"url": "https://i.ytimg.com/vi/dQw4w9WgXcQ/mqdefault.jpg"}
            }
        },
        "contentDetails": {
            "duration": "PT3M33S"
        },
        "statistics": {
            "viewCount": "1000000",
            "likeCount": "50000",
            "commentCount": "10000"
        }
    }

    result = scraper._parse_trending_video(video_data)

    # Verify ScrapedYouTubeVideo fields
    assert result.video_id == "dQw4w9WgXcQ"
    assert result.title == "Rick Astley - Never Gonna Give You Up"
    assert str(result.url) == "https://youtube.com/watch?v=dQw4w9WgXcQ"
    assert result.source_type == "youtube_trending"
    assert result.external_id == "dQw4w9WgXcQ"
    assert result.channel_id == "UCuAXFkgsw1L7xaCfnd5JJOw"
    assert result.channel_name == "Rick Astley"
    assert result.author == "Rick Astley"
    assert result.content == "The official video for Never Gonna Give You Up"
    assert str(result.thumbnail_url) == "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg"
    assert result.duration_seconds == 213  # 3m33s
    assert result.view_count == 1000000
    assert result.upvotes == 50000  # Maps to like_count
    assert result.comments_count == 10000
    assert result.tags == ["rick astley", "music", "80s"]
    assert result.published_at.year == 2009
    assert result.published_at.month == 10
    assert result.published_at.day == 25


def test_parse_trending_video_missing_optional_fields():
    """Test parsing video response with missing optional fields"""
    scraper = YouTubeTrendingScraper()

    # Minimal video data - no statistics, no tags, no maxres thumbnail
    video_data = {
        "id": "abc123",
        "snippet": {
            "publishedAt": "2024-01-15T10:30:00Z",
            "channelId": "UC_channel_123",
            "title": "Test Video",
            "description": "Test description",
            "channelTitle": "Test Channel",
            "thumbnails": {
                "high": {"url": "https://i.ytimg.com/vi/abc123/hqdefault.jpg"},
                "medium": {"url": "https://i.ytimg.com/vi/abc123/mqdefault.jpg"}
            }
        },
        "contentDetails": {
            "duration": "PT5M"
        }
    }

    result = scraper._parse_trending_video(video_data)

    # Verify required fields are present
    assert result.video_id == "abc123"
    assert result.title == "Test Video"
    assert result.channel_name == "Test Channel"

    # Verify optional fields use defaults or fallback values
    assert result.view_count == 0  # Default when statistics missing
    assert result.upvotes == 0
    assert result.comments_count == 0
    assert result.tags == []
    assert str(result.thumbnail_url) == "https://i.ytimg.com/vi/abc123/hqdefault.jpg"  # Fallback to high
    assert result.duration_seconds == 300  # 5 minutes
