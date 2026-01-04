from unittest.mock import AsyncMock, Mock

import pytest

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
    assert result.raw_data == video_data  # Raw data included


def test_parse_trending_video_invalid_data():
    """Test parsing returns None for invalid data without crashing"""
    scraper = YouTubeTrendingScraper()

    # Test missing required field (id)
    invalid_data_no_id = {
        "snippet": {
            "title": "Test",
            "publishedAt": "2024-01-15T10:30:00Z"
        }
    }
    result = scraper._parse_trending_video(invalid_data_no_id)
    assert result is None

    # Test invalid ISO timestamp
    invalid_data_bad_timestamp = {
        "id": "test123",
        "snippet": {
            "publishedAt": "invalid-timestamp",
            "title": "Test"
        }
    }
    result = scraper._parse_trending_video(invalid_data_bad_timestamp)
    assert result is None

    # Test None input
    result = scraper._parse_trending_video(None)
    assert result is None

    # Test empty dict
    result = scraper._parse_trending_video({})
    assert result is None

    # Test invalid input type
    result = scraper._parse_trending_video("not a dict")
    assert result is None


def test_filter_by_keywords():
    """Test filtering videos by keywords with relevance scoring"""
    scraper = YouTubeTrendingScraper()

    # Create mock videos with different keyword matches
    from app.schemas.scraped_article import ScrapedYouTubeVideo
    from datetime import datetime

    videos = [
        ScrapedYouTubeVideo(
            video_id="vid1",
            title="Learning Rust in 2024",
            url="https://youtube.com/watch?v=vid1",
            source_type="youtube_trending",
            external_id="vid1",
            content="A comprehensive guide to Rust programming language",
            author="Tech Channel",
            published_at=datetime.now(),
            channel_id="channel1",
            channel_name="Tech Channel",
            thumbnail_url="https://example.com/thumb1.jpg",
            duration_seconds=600,
            view_count=10000,
            tags=["rust", "programming", "tutorial"],
        ),
        ScrapedYouTubeVideo(
            video_id="vid2",
            title="Python Machine Learning Tutorial",
            url="https://youtube.com/watch?v=vid2",
            source_type="youtube_trending",
            external_id="vid2",
            content="Build ML models with Python and scikit-learn",
            author="AI Academy",
            published_at=datetime.now(),
            channel_id="channel2",
            channel_name="AI Academy",
            thumbnail_url="https://example.com/thumb2.jpg",
            duration_seconds=900,
            view_count=50000,
            tags=["python", "ml", "data science"],
        ),
        ScrapedYouTubeVideo(
            video_id="vid3",
            title="JavaScript React Tutorial",
            url="https://youtube.com/watch?v=vid3",
            source_type="youtube_trending",
            external_id="vid3",
            content="Learn React.js from scratch",
            author="Web Dev Pro",
            published_at=datetime.now(),
            channel_id="channel3",
            channel_name="Web Dev Pro",
            thumbnail_url="https://example.com/thumb3.jpg",
            duration_seconds=1200,
            view_count=30000,
            tags=["javascript", "react", "frontend"],
        ),
    ]

    keywords = [
        {"keyword": "rust", "weight": 5.0, "category": "programming"},
        {"keyword": "python", "weight": 4.0, "category": "programming"},
        {"keyword": "machine learning", "weight": 3.0, "category": "ai"},
    ]

    filtered = scraper._filter_by_keywords(videos, keywords)

    # Should return 2 videos (vid1 and vid2), vid3 has no matching keywords
    assert len(filtered) == 2

    # Video 1 should match "rust" only → score = 5.0
    vid1_result = next(v for v in filtered if v.video_id == "vid1")
    assert vid1_result.score == 5.0

    # Video 2 should match "python" + "machine learning" → score = 7.0
    vid2_result = next(v for v in filtered if v.video_id == "vid2")
    assert vid2_result.score == 7.0

    # Videos should be sorted by score (highest first)
    assert filtered[0].video_id == "vid2"
    assert filtered[1].video_id == "vid1"


def test_filter_by_keywords_minimum_threshold():
    """Test minimum keyword match requirement filters correctly"""
    scraper = YouTubeTrendingScraper()

    from app.schemas.scraped_article import ScrapedYouTubeVideo
    from datetime import datetime

    videos = [
        ScrapedYouTubeVideo(
            video_id="vid1",
            title="Advanced Rust Programming",
            url="https://youtube.com/watch?v=vid1",
            source_type="youtube_trending",
            external_id="vid1",
            content="Deep dive into Rust advanced features",
            author="Rust Expert",
            published_at=datetime.now(),
            channel_id="channel1",
            channel_name="Rust Expert",
            thumbnail_url="https://example.com/thumb1.jpg",
            duration_seconds=1800,
            view_count=20000,
            tags=["rust", "advanced"],
        ),
        ScrapedYouTubeVideo(
            video_id="vid2",
            title="Cooking Tutorial",
            url="https://youtube.com/watch?v=vid2",
            source_type="youtube_trending",
            external_id="vid2",
            content="How to cook delicious meals",
            author="Chef Channel",
            published_at=datetime.now(),
            channel_id="channel2",
            channel_name="Chef Channel",
            thumbnail_url="https://example.com/thumb2.jpg",
            duration_seconds=600,
            view_count=15000,
            tags=["cooking", "food"],
        ),
        ScrapedYouTubeVideo(
            video_id="vid3",
            title="YouTube Shorts - Quick Tip",
            url="https://youtube.com/watch?v=vid3",
            source_type="youtube_trending",
            external_id="vid3",
            content="A 30 second programming tip about Python",
            author="Quick Tips",
            published_at=datetime.now(),
            channel_id="channel3",
            channel_name="Quick Tips",
            thumbnail_url="https://example.com/thumb3.jpg",
            duration_seconds=30,  # Short video
            view_count=5000,
            tags=["python", "shorts"],
        ),
    ]

    keywords = [
        {"keyword": "rust", "weight": 5.0},
        {"keyword": "python", "weight": 4.0},
    ]

    # Test with default config (min_keyword_matches=1, no shorts filtering)
    filtered = scraper._filter_by_keywords(videos, keywords)
    assert len(filtered) == 2  # vid1 (rust) and vid3 (python)

    # Test with include_shorts=False - should exclude vid3
    config = {"include_shorts": False}
    filtered = scraper._filter_by_keywords(videos, keywords, config)
    assert len(filtered) == 1
    assert filtered[0].video_id == "vid1"

    # Test with min_view_count threshold
    config = {"min_view_count": 10000}
    filtered = scraper._filter_by_keywords(videos, keywords, config)
    assert len(filtered) == 1  # Only vid1 has >= 10000 views and matches keywords
    assert filtered[0].video_id == "vid1"

    # Test combined filters
    config = {"include_shorts": False, "min_view_count": 1000}
    filtered = scraper._filter_by_keywords(videos, keywords, config)
    assert len(filtered) == 1
    assert filtered[0].video_id == "vid1"
