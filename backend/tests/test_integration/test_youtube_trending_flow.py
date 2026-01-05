"""
Integration test for YouTube Trending scraper end-to-end workflow

Tests the complete flow with real database interaction:
1. Create keywords in database
2. Mock YouTube API responses
3. Initialize scraper with real dependencies
4. Execute scrape() method
5. Verify filtering, scoring, and deduplication
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session

from app.scrapers.plugins.youtube_trending import YouTubeTrendingScraper
from app.models.keyword import Keyword
from app.youtube.quota_manager import YouTubeQuotaManager


@pytest.fixture
def setup_keywords(db_session: Session):
    """Create test keywords in database"""
    keywords = [
        Keyword(keyword="rust", weight=5.0, category="programming", is_active=True),
        Keyword(keyword="python", weight=4.0, category="programming", is_active=True),
        Keyword(keyword="typescript", weight=3.0, category="programming", is_active=True),
    ]
    for kw in keywords:
        db_session.add(kw)
    db_session.commit()

    return keywords


@pytest.fixture
def mock_youtube_api_response():
    """Realistic YouTube API response with 3 videos"""
    return {
        "items": [
            # Video 1: Matches "rust" keyword
            {
                "id": "rust_video_123",
                "snippet": {
                    "title": "Rust Programming Tutorial for Beginners",
                    "description": "Learn Rust programming language from scratch. This comprehensive tutorial covers ownership, borrowing, and more.",
                    "channelId": "UC_rust_channel",
                    "channelTitle": "Rust Academy",
                    "publishedAt": "2024-01-01T10:00:00Z",
                    "tags": ["rust", "programming", "tutorial"],
                    "thumbnails": {
                        "high": {"url": "https://i.ytimg.com/vi/rust_video_123/hqdefault.jpg"}
                    }
                },
                "contentDetails": {
                    "duration": "PT15M30S"  # 15 minutes 30 seconds
                },
                "statistics": {
                    "viewCount": "50000",
                    "likeCount": "2500",
                    "commentCount": "350"
                }
            },
            # Video 2: Matches "python" keyword
            {
                "id": "python_video_456",
                "snippet": {
                    "title": "Python Data Science Project",
                    "description": "Build a complete data science project using Python, pandas, and scikit-learn.",
                    "channelId": "UC_python_channel",
                    "channelTitle": "Python Experts",
                    "publishedAt": "2024-01-02T14:00:00Z",
                    "tags": ["python", "data-science", "tutorial"],
                    "thumbnails": {
                        "maxres": {"url": "https://i.ytimg.com/vi/python_video_456/maxresdefault.jpg"}
                    }
                },
                "contentDetails": {
                    "duration": "PT25M45S"  # 25 minutes 45 seconds
                },
                "statistics": {
                    "viewCount": "75000",
                    "likeCount": "3200",
                    "commentCount": "480"
                }
            },
            # Video 3: Matches "rust" AND "python" keywords
            {
                "id": "multi_lang_789",
                "snippet": {
                    "title": "Rust vs Python Performance Comparison",
                    "description": "Comparing Rust and Python performance for various use cases. Which language should you choose?",
                    "channelId": "UC_multi_channel",
                    "channelTitle": "Tech Comparisons",
                    "publishedAt": "2024-01-03T09:00:00Z",
                    "tags": ["rust", "python", "performance", "comparison"],
                    "thumbnails": {
                        "high": {"url": "https://i.ytimg.com/vi/multi_lang_789/hqdefault.jpg"}
                    }
                },
                "contentDetails": {
                    "duration": "PT18M20S"  # 18 minutes 20 seconds
                },
                "statistics": {
                    "viewCount": "120000",
                    "likeCount": "5800",
                    "commentCount": "920"
                }
            },
            # Video 4: Does NOT match any keyword (should be filtered out)
            {
                "id": "javascript_video_999",
                "snippet": {
                    "title": "JavaScript Framework Comparison 2024",
                    "description": "Comparing React, Vue, and Angular for modern web development.",
                    "channelId": "UC_js_channel",
                    "channelTitle": "Frontend Masters",
                    "publishedAt": "2024-01-04T12:00:00Z",
                    "tags": ["javascript", "react", "vue"],
                    "thumbnails": {
                        "high": {"url": "https://i.ytimg.com/vi/javascript_video_999/hqdefault.jpg"}
                    }
                },
                "contentDetails": {
                    "duration": "PT22M10S"
                },
                "statistics": {
                    "viewCount": "60000",
                    "likeCount": "2800",
                    "commentCount": "410"
                }
            },
            # Video 5: YouTube Short (under 60 seconds)
            {
                "id": "short_video_111",
                "snippet": {
                    "title": "Quick Python Tip #shorts",
                    "description": "Python tip of the day",
                    "channelId": "UC_tips_channel",
                    "channelTitle": "Quick Tips",
                    "publishedAt": "2024-01-05T08:00:00Z",
                    "tags": ["python", "shorts", "tips"],
                    "thumbnails": {
                        "high": {"url": "https://i.ytimg.com/vi/short_video_111/hqdefault.jpg"}
                    }
                },
                "contentDetails": {
                    "duration": "PT45S"  # 45 seconds (YouTube Short)
                },
                "statistics": {
                    "viewCount": "15000",
                    "likeCount": "800",
                    "commentCount": "50"
                }
            }
        ]
    }


@pytest.mark.asyncio
async def test_youtube_trending_end_to_end(
    db_session: Session,
    setup_keywords,
    mock_youtube_api_response,
    redis_client
):
    """
    Test complete YouTube Trending scraper workflow with database integration

    Verifies:
    - Keyword filtering from database
    - Video parsing and scoring
    - Quota manager integration
    - Correct source_type assignment
    - Filtering logic (shorts, view count, keyword matches)
    """
    # Prepare keyword data from database (simulating how scraping task would fetch them)
    keyword_data = [
        {"keyword": kw.keyword, "weight": kw.weight, "category": kw.category}
        for kw in setup_keywords
    ]

    # Initialize scraper with real Redis client
    scraper = YouTubeTrendingScraper(redis_client=redis_client)

    # Mock YouTube API client
    mock_youtube = Mock()
    mock_request = Mock()
    mock_execute = Mock(return_value=mock_youtube_api_response)

    mock_request.execute = mock_execute
    mock_youtube.videos().list.return_value = mock_request

    scraper.youtube = mock_youtube

    # Mock quota manager to allow scraping (async methods)
    mock_quota_manager = Mock(spec=YouTubeQuotaManager)
    mock_quota_manager.check_quota = AsyncMock(return_value=True)
    mock_quota_manager.record_usage = AsyncMock()

    scraper.quota_manager = mock_quota_manager

    # Prepare config
    config = {
        "region_code": "US",
        "max_results": 50,
        "video_category": "28",  # Science & Technology
        "include_shorts": True,  # Include shorts by default
        "min_view_count": 0,
        "min_keyword_matches": 1
    }

    # Execute scraper
    results = await scraper.scrape(config, keyword_data)

    # Verify quota was checked and recorded
    mock_quota_manager.check_quota.assert_called_once()
    mock_quota_manager.record_usage.assert_called_once_with(100)

    # Verify YouTube API was called correctly
    mock_youtube.videos().list.assert_called_once_with(
        part='snippet,contentDetails,statistics',
        chart='mostPopular',
        videoCategoryId='28',
        regionCode='US',
        maxResults=50
    )

    # Verify results
    assert len(results) == 4, f"Should return 4 videos (got {len(results)})"

    # All results should have source_type set correctly
    assert all(v.source_type == "youtube_trending" for v in results)

    # All results should have score attribute
    assert all(hasattr(v, 'score') for v in results)

    # Results should be sorted by score (highest first)
    scores = [v.score for v in results]
    assert scores == sorted(scores, reverse=True), "Results should be sorted by score descending"

    # Video matching both "rust" and "python" should have highest score
    # rust (5.0) + python (4.0) = 9.0
    top_video = results[0]
    assert top_video.video_id == "multi_lang_789", f"Top video should be multi_lang_789, got {top_video.video_id}"
    assert top_video.score == 9.0, f"Top video score should be 9.0, got {top_video.score}"
    assert "rust" in top_video.title.lower()
    assert "python" in top_video.title.lower()

    # Second video should match "rust" only (score = 5.0)
    second_video = results[1]
    assert second_video.video_id == "rust_video_123", f"Second video should be rust_video_123, got {second_video.video_id}"
    assert second_video.score == 5.0, f"Second video score should be 5.0, got {second_video.score}"

    # Third and fourth videos match "python" only (score = 4.0 each)
    # Could be either python_video_456 or short_video_111 in any order
    remaining_videos = results[2:4]
    remaining_ids = {v.video_id for v in remaining_videos}
    assert "python_video_456" in remaining_ids
    assert "short_video_111" in remaining_ids
    assert all(v.score == 4.0 for v in remaining_videos)

    # JavaScript video should NOT be in results (no matching keywords)
    video_ids = [v.video_id for v in results]
    assert "javascript_video_999" not in video_ids

    # Verify all videos have required fields populated
    for video in results:
        assert video.title
        assert str(video.url).startswith("https://youtube.com/watch?v=")
        assert video.video_id
        assert video.channel_id
        assert video.channel_name
        assert video.published_at
        assert video.view_count is not None
        assert video.upvotes is not None  # like_count
        assert video.comments_count is not None


@pytest.mark.asyncio
async def test_youtube_scraping_filters_shorts(
    db_session: Session,
    setup_keywords,
    mock_youtube_api_response,
    redis_client
):
    """Test that shorts can be filtered out when include_shorts=False"""

    keyword_data = [
        {"keyword": kw.keyword, "weight": kw.weight, "category": kw.category}
        for kw in setup_keywords
    ]

    scraper = YouTubeTrendingScraper(redis_client=redis_client)

    # Mock YouTube API
    mock_youtube = Mock()
    mock_request = Mock()
    mock_request.execute = Mock(return_value=mock_youtube_api_response)
    mock_youtube.videos().list.return_value = mock_request
    scraper.youtube = mock_youtube

    # Mock quota manager
    mock_quota_manager = Mock(spec=YouTubeQuotaManager)
    mock_quota_manager.check_quota = AsyncMock(return_value=True)
    mock_quota_manager.record_usage = AsyncMock()
    scraper.quota_manager = mock_quota_manager

    # Config with shorts excluded
    config = {
        "region_code": "US",
        "max_results": 50,
        "video_category": "28",
        "include_shorts": False,  # Exclude shorts
        "min_view_count": 0,
        "min_keyword_matches": 1
    }

    results = await scraper.scrape(config, keyword_data)

    # Should have 3 results (excluding the 45-second short)
    assert len(results) == 3

    # Verify short is not in results
    video_ids = [v.video_id for v in results]
    assert "short_video_111" not in video_ids

    # All remaining videos should be longer than 60 seconds
    for video in results:
        assert video.duration_seconds is None or video.duration_seconds >= 60


@pytest.mark.asyncio
async def test_youtube_scraping_respects_min_view_count(
    db_session: Session,
    setup_keywords,
    mock_youtube_api_response,
    redis_client
):
    """Test that videos below min_view_count threshold are filtered out"""

    keyword_data = [
        {"keyword": kw.keyword, "weight": kw.weight, "category": kw.category}
        for kw in setup_keywords
    ]

    scraper = YouTubeTrendingScraper(redis_client=redis_client)

    # Mock YouTube API
    mock_youtube = Mock()
    mock_request = Mock()
    mock_request.execute = Mock(return_value=mock_youtube_api_response)
    mock_youtube.videos().list.return_value = mock_request
    scraper.youtube = mock_youtube

    # Mock quota manager
    mock_quota_manager = Mock(spec=YouTubeQuotaManager)
    mock_quota_manager.check_quota = AsyncMock(return_value=True)
    mock_quota_manager.record_usage = AsyncMock()
    scraper.quota_manager = mock_quota_manager

    # Config with high view count threshold
    config = {
        "region_code": "US",
        "max_results": 50,
        "video_category": "28",
        "include_shorts": True,
        "min_view_count": 60000,  # Filter out videos with < 60k views
        "min_keyword_matches": 1
    }

    results = await scraper.scrape(config, keyword_data)

    # Only 2 videos should pass: python_video_456 (75k) and multi_lang_789 (120k)
    assert len(results) == 2

    # Verify all results have >= 60k views
    for video in results:
        assert video.view_count >= 60000

    # Verify specific videos
    video_ids = [v.video_id for v in results]
    assert "python_video_456" in video_ids
    assert "multi_lang_789" in video_ids
    assert "rust_video_123" not in video_ids  # 50k views (below threshold)
    assert "short_video_111" not in video_ids  # 15k views (below threshold)


@pytest.mark.asyncio
async def test_youtube_scraping_quota_exhausted(
    db_session: Session,
    setup_keywords,
    redis_client
):
    """Test that scraper returns empty list when quota is exhausted"""

    keyword_data = [
        {"keyword": kw.keyword, "weight": kw.weight, "category": kw.category}
        for kw in setup_keywords
    ]

    scraper = YouTubeTrendingScraper(redis_client=redis_client)

    # Mock YouTube API (should NOT be called)
    mock_youtube = Mock()
    scraper.youtube = mock_youtube

    # Mock quota manager to indicate quota exhausted
    mock_quota_manager = Mock(spec=YouTubeQuotaManager)
    mock_quota_manager.check_quota = AsyncMock(return_value=False)  # Quota exhausted
    mock_quota_manager.record_usage = AsyncMock()
    scraper.quota_manager = mock_quota_manager

    config = {
        "region_code": "US",
        "max_results": 50,
        "video_category": "28"
    }

    results = await scraper.scrape(config, keyword_data)

    # Should return empty list
    assert results == []

    # Quota check should have been called
    mock_quota_manager.check_quota.assert_called_once()

    # YouTube API should NOT have been called
    mock_youtube.videos.assert_not_called()

    # Record usage should NOT have been called (no API call made)
    mock_quota_manager.record_usage.assert_not_called()


@pytest.mark.asyncio
async def test_youtube_scraping_deduplication(
    db_session: Session,
    setup_keywords,
    mock_youtube_api_response,
    redis_client
):
    """
    Test that running scraper twice with same data doesn't create duplicates

    Note: This tests the scraper's consistency, not database deduplication
    (database deduplication is handled by the article saving logic)
    """

    keyword_data = [
        {"keyword": kw.keyword, "weight": kw.weight, "category": kw.category}
        for kw in setup_keywords
    ]

    scraper = YouTubeTrendingScraper(redis_client=redis_client)

    # Mock YouTube API
    mock_youtube = Mock()
    mock_request = Mock()
    mock_request.execute = Mock(return_value=mock_youtube_api_response)
    mock_youtube.videos().list.return_value = mock_request
    scraper.youtube = mock_youtube

    # Mock quota manager
    mock_quota_manager = Mock(spec=YouTubeQuotaManager)
    mock_quota_manager.check_quota = AsyncMock(return_value=True)
    mock_quota_manager.record_usage = AsyncMock()
    scraper.quota_manager = mock_quota_manager

    config = {
        "region_code": "US",
        "max_results": 50,
        "video_category": "28",
        "include_shorts": True,
        "min_view_count": 0,
        "min_keyword_matches": 1
    }

    # First scrape
    results_1 = await scraper.scrape(config, keyword_data)

    # Second scrape (same data)
    results_2 = await scraper.scrape(config, keyword_data)

    # Results should be identical
    assert len(results_1) == len(results_2)

    # Video IDs should match
    video_ids_1 = {v.video_id for v in results_1}
    video_ids_2 = {v.video_id for v in results_2}
    assert video_ids_1 == video_ids_2

    # Scores should match
    scores_1 = {v.video_id: v.score for v in results_1}
    scores_2 = {v.video_id: v.score for v in results_2}
    assert scores_1 == scores_2

    # URLs should be identical (external_id used for deduplication at DB level)
    for v1, v2 in zip(results_1, results_2):
        assert v1.external_id == v2.external_id
        assert v1.url == v2.url


@pytest.mark.asyncio
async def test_youtube_scraping_with_no_keywords(
    db_session: Session,
    mock_youtube_api_response,
    redis_client
):
    """Test that scraper returns empty list when no keywords provided"""

    scraper = YouTubeTrendingScraper(redis_client=redis_client)

    # Mock YouTube API
    mock_youtube = Mock()
    mock_request = Mock()
    mock_request.execute = Mock(return_value=mock_youtube_api_response)
    mock_youtube.videos().list.return_value = mock_request
    scraper.youtube = mock_youtube

    # Mock quota manager
    mock_quota_manager = Mock(spec=YouTubeQuotaManager)
    mock_quota_manager.check_quota = AsyncMock(return_value=True)
    mock_quota_manager.record_usage = AsyncMock()
    scraper.quota_manager = mock_quota_manager

    config = {
        "region_code": "US",
        "max_results": 50,
        "video_category": "28"
    }

    # Scrape with empty keyword list
    results = await scraper.scrape(config, [])

    # Should return empty list (no keywords to match)
    assert results == []

    # API should still have been called (quota recorded)
    mock_quota_manager.check_quota.assert_called_once()
    mock_quota_manager.record_usage.assert_called_once_with(100)
