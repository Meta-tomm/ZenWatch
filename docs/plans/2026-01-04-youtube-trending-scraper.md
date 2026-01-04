# YouTube Trending Scraper Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the YouTube Trending scraper stub to fetch and filter trending tech videos using YouTube Data API v3

**Architecture:** Extend existing YouTubeTrendingScraper with API calls to videos.list (chart=mostPopular), parse responses to ScrapedYouTubeVideo objects, filter by user keywords, integrate with quota manager, and schedule via Celery

**Tech Stack:** Python 3.11+, FastAPI, YouTube Data API v3, google-api-python-client, isodate (duration parsing), Redis (quota tracking), Celery (scheduling), pytest

---

## Task 1: Add isodate Dependency

**Files:**
- Modify: `backend/pyproject.toml:24-30` (dependencies section)
- Modify: `backend/poetry.lock` (auto-generated)

**Step 1: Add isodate to dependencies**

Edit `backend/pyproject.toml`:

```toml
[tool.poetry.dependencies]
# ... existing dependencies ...
isodate = "^0.6.1"
```

**Step 2: Install dependency**

Run: `poetry add isodate`
Expected: "Using version ^0.6.1 for isodate"

**Step 3: Verify installation**

Run: `poetry show isodate`
Expected: Shows isodate package info

**Step 4: Commit**

```bash
git add pyproject.toml poetry.lock
git commit -m "chore(deps): add isodate for ISO 8601 duration parsing"
```

---

## Task 2: Test - ISO 8601 Duration Parsing Helper

**Files:**
- Create: `backend/tests/test_scrapers/test_youtube_trending.py`
- Test: Unit test for duration parsing

**Step 1: Write failing test for duration parsing**

Create test in `backend/tests/test_scrapers/test_youtube_trending.py`:

```python
import pytest
from app.scrapers.plugins.youtube_trending import YouTubeTrendingScraper


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
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_parse_iso8601_duration -v`
Expected: FAIL with "AttributeError: 'YouTubeTrendingScraper' object has no attribute '_parse_duration'"

**Step 3: Implement _parse_duration method**

Add to `backend/app/scrapers/plugins/youtube_trending.py`:

```python
import isodate
from typing import Optional


def _parse_duration(self, iso_duration: Optional[str]) -> Optional[int]:
    """
    Parse ISO 8601 duration to seconds.

    Args:
        iso_duration: ISO 8601 duration string (e.g., "PT4M13S")

    Returns:
        Duration in seconds, or None if parsing fails
    """
    if not iso_duration:
        return None

    try:
        duration = isodate.parse_duration(iso_duration)
        return int(duration.total_seconds())
    except Exception as e:
        self.logger.warning(f"Failed to parse duration '{iso_duration}': {e}")
        return None
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_parse_iso8601_duration -v`
Expected: PASS (2/2 tests)

**Step 5: Commit**

```bash
git add tests/test_scrapers/test_youtube_trending.py app/scrapers/plugins/youtube_trending.py
git commit -m "feat(scrapers): add ISO 8601 duration parsing to YouTube Trending"
```

---

## Task 3: Test - Parse Trending Video Response

**Files:**
- Modify: `backend/tests/test_scrapers/test_youtube_trending.py`
- Modify: `backend/app/scrapers/plugins/youtube_trending.py`

**Step 1: Write failing test for _parse_trending_video**

Add to `tests/test_scrapers/test_youtube_trending.py`:

```python
from datetime import datetime


def test_parse_trending_video():
    """Test parsing YouTube API response to ScrapedYouTubeVideo"""
    scraper = YouTubeTrendingScraper()

    # Mock YouTube API response structure
    video_item = {
        'id': 'dQw4w9WgXcQ',
        'snippet': {
            'title': 'Building a Blockchain in Python',
            'description': 'Learn how to build a blockchain from scratch',
            'channelId': 'UC_x5XG1OV2P6uZZ5FSM9Ttw',
            'channelTitle': 'Tech Guru',
            'publishedAt': '2024-01-01T10:00:00Z',
            'tags': ['python', 'blockchain', 'tutorial'],
            'thumbnails': {
                'maxres': {'url': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'},
                'high': {'url': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/hqdefault.jpg'}
            }
        },
        'contentDetails': {
            'duration': 'PT15M30S'
        },
        'statistics': {
            'viewCount': '50000',
            'likeCount': '2000',
            'commentCount': '150'
        }
    }

    result = scraper._parse_trending_video(video_item)

    # Verify ScrapedYouTubeVideo fields
    assert result.video_id == 'dQw4w9WgXcQ'
    assert result.title == 'Building a Blockchain in Python'
    assert result.channel_id == 'UC_x5XG1OV2P6uZZ5FSM9Ttw'
    assert result.channel_name == 'Tech Guru'
    assert result.duration_seconds == 930  # 15min 30sec
    assert result.view_count == 50000
    assert result.thumbnail_url == 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
    assert result.source_type == 'youtube_trending'
    assert 'python' in result.tags
    assert 'blockchain' in result.tags


def test_parse_trending_video_missing_optional_fields():
    """Test parsing with missing optional fields (stats, thumbnail)"""
    scraper = YouTubeTrendingScraper()

    video_item = {
        'id': 'abc123',
        'snippet': {
            'title': 'Test Video',
            'description': 'Test description',
            'channelId': 'UCtest',
            'channelTitle': 'Test Channel',
            'publishedAt': '2024-01-01T10:00:00Z',
            'thumbnails': {}  # Empty thumbnails
        },
        'contentDetails': {
            'duration': 'PT5M'
        }
        # No statistics field
    }

    result = scraper._parse_trending_video(video_item)

    assert result.video_id == 'abc123'
    assert result.view_count is None
    assert result.thumbnail_url is None  # No thumbnails available
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_parse_trending_video -v`
Expected: FAIL with "AttributeError: 'YouTubeTrendingScraper' object has no attribute '_parse_trending_video'"

**Step 3: Implement _parse_trending_video method**

Add to `backend/app/scrapers/plugins/youtube_trending.py`:

```python
from typing import Dict, Any
from datetime import datetime
from app.schemas.scraped_article import ScrapedYouTubeVideo


def _parse_trending_video(self, video_item: Dict[str, Any]) -> ScrapedYouTubeVideo:
    """
    Parse YouTube API video item to ScrapedYouTubeVideo.

    Args:
        video_item: YouTube API videos.list response item

    Returns:
        ScrapedYouTubeVideo object
    """
    snippet = video_item['snippet']
    video_id = video_item['id']

    # Extract thumbnail (prefer maxres > high > medium)
    thumbnails = snippet.get('thumbnails', {})
    thumbnail_url = None
    for quality in ['maxres', 'high', 'medium']:
        if quality in thumbnails:
            thumbnail_url = thumbnails[quality]['url']
            break

    # Parse duration
    duration_iso = video_item.get('contentDetails', {}).get('duration')
    duration_seconds = self._parse_duration(duration_iso)

    # Extract statistics (optional)
    stats = video_item.get('statistics', {})
    view_count = int(stats['viewCount']) if 'viewCount' in stats else None
    like_count = int(stats.get('likeCount', 0))
    comment_count = int(stats.get('commentCount', 0))

    # Parse published date
    published_str = snippet['publishedAt']
    published_at = datetime.fromisoformat(published_str.replace('Z', '+00:00'))

    return ScrapedYouTubeVideo(
        title=snippet['title'],
        url=f"https://www.youtube.com/watch?v={video_id}",
        source_type='youtube_trending',
        external_id=video_id,
        content=snippet.get('description', ''),
        author=snippet['channelTitle'],
        published_at=published_at,
        tags=snippet.get('tags', []),
        video_id=video_id,
        channel_id=snippet['channelId'],
        channel_name=snippet['channelTitle'],
        thumbnail_url=thumbnail_url,
        duration_seconds=duration_seconds,
        view_count=view_count
    )
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_parse_trending_video -v`
Expected: PASS (2/2 tests)

**Step 5: Commit**

```bash
git add tests/test_scrapers/test_youtube_trending.py app/scrapers/plugins/youtube_trending.py
git commit -m "feat(scrapers): implement trending video response parsing"
```

---

## Task 4: Test - Keyword Filtering

**Files:**
- Modify: `backend/tests/test_scrapers/test_youtube_trending.py`
- Modify: `backend/app/scrapers/plugins/youtube_trending.py`

**Step 1: Write failing test for keyword filtering**

Add to `tests/test_scrapers/test_youtube_trending.py`:

```python
def test_filter_by_keywords():
    """Test keyword filtering logic"""
    scraper = YouTubeTrendingScraper()

    from app.schemas.scraped_article import ScrapedYouTubeVideo
    from datetime import datetime, timezone

    video1 = ScrapedYouTubeVideo(
        title="Building a Blockchain with Python",
        url="https://youtube.com/watch?v=1",
        source_type='youtube_trending',
        external_id='vid1',
        content="Learn blockchain development with Python",
        author="Tech Channel",
        published_at=datetime.now(timezone.utc),
        tags=['python', 'blockchain'],
        video_id='vid1',
        channel_id='ch1',
        channel_name="Tech Channel"
    )

    video2 = ScrapedYouTubeVideo(
        title="Cooking Tutorial",
        url="https://youtube.com/watch?v=2",
        source_type='youtube_trending',
        external_id='vid2',
        content="How to cook pasta",
        author="Food Channel",
        published_at=datetime.now(timezone.utc),
        tags=['cooking', 'food'],
        video_id='vid2',
        channel_id='ch2',
        channel_name="Food Channel"
    )

    videos = [video1, video2]
    keywords = ['python', 'blockchain', 'AI']

    # Filter with keywords
    filtered = scraper._filter_by_keywords(videos, keywords)

    assert len(filtered) == 1
    assert filtered[0].video_id == 'vid1'


def test_filter_by_keywords_empty():
    """Test filtering with no keywords returns all videos"""
    scraper = YouTubeTrendingScraper()

    from app.schemas.scraped_article import ScrapedYouTubeVideo
    from datetime import datetime, timezone

    video = ScrapedYouTubeVideo(
        title="Test Video",
        url="https://youtube.com/watch?v=1",
        source_type='youtube_trending',
        external_id='vid1',
        content="Test content",
        author="Test Channel",
        published_at=datetime.now(timezone.utc),
        tags=[],
        video_id='vid1',
        channel_id='ch1',
        channel_name="Test Channel"
    )

    # No keywords = return all
    filtered = scraper._filter_by_keywords([video], [])
    assert len(filtered) == 1
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_filter_by_keywords -v`
Expected: FAIL with "AttributeError: 'YouTubeTrendingScraper' object has no attribute '_filter_by_keywords'"

**Step 3: Implement _filter_by_keywords method**

Add to `backend/app/scrapers/plugins/youtube_trending.py`:

```python
from typing import List
from app.schemas.scraped_article import ScrapedYouTubeVideo


def _filter_by_keywords(
    self,
    videos: List[ScrapedYouTubeVideo],
    keywords: List[str]
) -> List[ScrapedYouTubeVideo]:
    """
    Filter videos by keyword matching in title, description, and tags.

    Args:
        videos: List of scraped videos
        keywords: List of keywords to match (case-insensitive)

    Returns:
        Filtered list of videos matching at least one keyword
    """
    if not keywords:
        return videos

    keywords_lower = [kw.lower() for kw in keywords]
    filtered = []

    for video in videos:
        # Check title, content, and tags
        search_text = f"{video.title} {video.content} {' '.join(video.tags or [])}".lower()

        # Match if any keyword found
        if any(kw in search_text for kw in keywords_lower):
            filtered.append(video)

    return filtered
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_filter_by_keywords -v`
Expected: PASS (2/2 tests)

**Step 5: Commit**

```bash
git add tests/test_scrapers/test_youtube_trending.py app/scrapers/plugins/youtube_trending.py
git commit -m "feat(scrapers): implement keyword filtering for trending videos"
```

---

## Task 5: Test - YouTube API Call with Mocking

**Files:**
- Modify: `backend/tests/test_scrapers/test_youtube_trending.py`
- Modify: `backend/app/scrapers/plugins/youtube_trending.py`

**Step 1: Write failing test for API call**

Add to `tests/test_scrapers/test_youtube_trending.py`:

```python
from unittest.mock import Mock, patch, MagicMock


def test_fetch_trending_videos_api_call():
    """Test YouTube API call for trending videos"""
    with patch('app.scrapers.plugins.youtube_trending.build') as mock_build:
        # Mock YouTube API client
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock API response
        mock_response = {
            'items': [
                {
                    'id': 'video1',
                    'snippet': {
                        'title': 'Tech Video',
                        'description': 'About tech',
                        'channelId': 'ch1',
                        'channelTitle': 'Channel 1',
                        'publishedAt': '2024-01-01T10:00:00Z',
                        'tags': ['tech'],
                        'thumbnails': {'high': {'url': 'http://example.com/thumb.jpg'}}
                    },
                    'contentDetails': {'duration': 'PT5M'},
                    'statistics': {'viewCount': '1000', 'likeCount': '50', 'commentCount': '10'}
                }
            ]
        }

        mock_youtube.videos().list().execute.return_value = mock_response

        # Create scraper
        scraper = YouTubeTrendingScraper(redis_client=Mock())
        scraper.youtube = mock_youtube

        # Call method
        videos = scraper._fetch_trending_videos({'region_code': 'US', 'max_results': 50})

        # Verify API was called correctly
        mock_youtube.videos().list.assert_called_once_with(
            part='snippet,contentDetails,statistics',
            chart='mostPopular',
            regionCode='US',
            videoCategoryId='28',  # Science & Technology
            maxResults=50
        )

        # Verify result
        assert len(videos) == 1
        assert videos[0].video_id == 'video1'
        assert videos[0].title == 'Tech Video'


def test_fetch_trending_videos_api_error():
    """Test API error handling"""
    from googleapiclient.errors import HttpError

    with patch('app.scrapers.plugins.youtube_trending.build') as mock_build:
        mock_youtube = MagicMock()
        mock_build.return_value = mock_youtube

        # Mock HTTP 403 error
        mock_youtube.videos().list().execute.side_effect = HttpError(
            resp=Mock(status=403),
            content=b'Forbidden'
        )

        scraper = YouTubeTrendingScraper(redis_client=Mock())
        scraper.youtube = mock_youtube

        # Should return empty list on error
        videos = scraper._fetch_trending_videos({'region_code': 'US', 'max_results': 50})
        assert videos == []
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_fetch_trending_videos_api_call -v`
Expected: FAIL with "AttributeError: 'YouTubeTrendingScraper' object has no attribute '_fetch_trending_videos'"

**Step 3: Implement _fetch_trending_videos method**

Add to `backend/app/scrapers/plugins/youtube_trending.py`:

```python
from googleapiclient.errors import HttpError


def _fetch_trending_videos(self, config: Dict) -> List[ScrapedYouTubeVideo]:
    """
    Fetch trending videos from YouTube API.

    Args:
        config: Scraper configuration with region_code, max_results

    Returns:
        List of parsed ScrapedYouTubeVideo objects
    """
    if not self.youtube:
        self.logger.error("YouTube API client not initialized")
        return []

    try:
        # Call YouTube API
        request = self.youtube.videos().list(
            part='snippet,contentDetails,statistics',
            chart='mostPopular',
            regionCode=config.get('region_code', 'US'),
            videoCategoryId='28',  # Science & Technology
            maxResults=config.get('max_results', 50)
        )

        response = request.execute()

        # Parse videos
        videos = []
        for item in response.get('items', []):
            try:
                video = self._parse_trending_video(item)
                videos.append(video)
            except Exception as e:
                self.logger.warning(f"Failed to parse video: {e}")
                continue

        self.logger.info(f"Fetched {len(videos)} trending videos")
        return videos

    except HttpError as e:
        self.logger.error(f"YouTube API error: {e}")
        return []
    except Exception as e:
        self.logger.error(f"Unexpected error fetching trending videos: {e}")
        return []
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_fetch_trending_videos_api_call -v`
Expected: PASS (2/2 tests)

**Step 5: Commit**

```bash
git add tests/test_scrapers/test_youtube_trending.py app/scrapers/plugins/youtube_trending.py
git commit -m "feat(scrapers): implement YouTube API call for trending videos"
```

---

## Task 6: Test - Quota Management Integration

**Files:**
- Modify: `backend/tests/test_scrapers/test_youtube_trending.py`
- Modify: `backend/app/scrapers/plugins/youtube_trending.py`

**Step 1: Write failing test for quota checking**

Add to `tests/test_scrapers/test_youtube_trending.py`:

```python
import pytest


@pytest.mark.asyncio
async def test_scrape_checks_quota_before_api_call():
    """Test that scraper checks quota before making API calls"""
    from fakeredis import FakeRedis

    redis_client = FakeRedis(decode_responses=True)
    scraper = YouTubeTrendingScraper(redis_client=redis_client)

    # Mock quota manager to return False (quota exhausted)
    with patch.object(scraper.quota_manager, 'check_quota', return_value=False):
        result = await scraper.scrape({'region_code': 'US'}, ['python'])

        # Should return empty list without calling API
        assert result == []


@pytest.mark.asyncio
async def test_scrape_records_quota_usage():
    """Test that scraper records quota usage after API call"""
    from fakeredis import FakeRedis

    redis_client = FakeRedis(decode_responses=True)
    scraper = YouTubeTrendingScraper(redis_client=redis_client)

    # Mock API call
    with patch.object(scraper, '_fetch_trending_videos', return_value=[]):
        with patch.object(scraper.quota_manager, 'check_quota', return_value=True):
            with patch.object(scraper.quota_manager, 'record_usage') as mock_record:
                await scraper.scrape({'region_code': 'US'}, ['python'])

                # Should record 100 units usage
                mock_record.assert_called_once_with(100)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_scrape_checks_quota_before_api_call -v`
Expected: FAIL (scrape method not implemented with quota checks)

**Step 3: Implement main scrape method with quota management**

Update `scrape()` method in `backend/app/scrapers/plugins/youtube_trending.py`:

```python
async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedYouTubeVideo]:
    """
    Scrape trending videos from YouTube with quota management.

    Args:
        config: Scraper configuration (region_code, max_results, etc.)
        keywords: List of keywords to filter videos

    Returns:
        List of trending videos matching keywords
    """
    # Check quota availability
    if self.quota_manager and not await self.quota_manager.check_quota():
        self.logger.warning("YouTube API quota exhausted, skipping trending scrape")
        return []

    # Fetch trending videos from API
    videos = self._fetch_trending_videos(config)

    # Record quota usage (100 units per call)
    if self.quota_manager:
        await self.quota_manager.record_usage(100)

    # Filter by keywords
    if keywords:
        videos = self._filter_by_keywords(videos, keywords)
        self.logger.info(f"Filtered to {len(videos)} videos matching keywords")

    return videos
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_scrapers/test_youtube_trending.py::test_scrape_checks_quota_before_api_call -v`
Expected: PASS (2/2 tests)

**Step 5: Commit**

```bash
git add tests/test_scrapers/test_youtube_trending.py app/scrapers/plugins/youtube_trending.py
git commit -m "feat(scrapers): integrate quota management in trending scraper"
```

---

## Task 7: Integration Test - Full Scraping Flow

**Files:**
- Create: `backend/tests/test_integration/test_youtube_trending_flow.py`

**Step 1: Write integration test**

Create `tests/test_integration/test_youtube_trending_flow.py`:

```python
import pytest
from unittest.mock import patch, MagicMock
from fakeredis import FakeRedis
from app.scrapers.plugins.youtube_trending import YouTubeTrendingScraper


@pytest.mark.asyncio
async def test_full_trending_scraping_flow():
    """Test complete flow: API call → parse → filter → return"""

    # Setup
    redis_client = FakeRedis(decode_responses=True)

    # Mock YouTube API response
    mock_api_response = {
        'items': [
            {
                'id': 'vid1',
                'snippet': {
                    'title': 'Python Blockchain Tutorial',
                    'description': 'Learn blockchain with Python',
                    'channelId': 'ch1',
                    'channelTitle': 'Tech Channel',
                    'publishedAt': '2024-01-01T10:00:00Z',
                    'tags': ['python', 'blockchain'],
                    'thumbnails': {'high': {'url': 'http://example.com/1.jpg'}}
                },
                'contentDetails': {'duration': 'PT10M'},
                'statistics': {'viewCount': '5000', 'likeCount': '200', 'commentCount': '50'}
            },
            {
                'id': 'vid2',
                'snippet': {
                    'title': 'Cooking Pasta',
                    'description': 'How to cook Italian pasta',
                    'channelId': 'ch2',
                    'channelTitle': 'Food Channel',
                    'publishedAt': '2024-01-01T11:00:00Z',
                    'tags': ['cooking', 'food'],
                    'thumbnails': {'high': {'url': 'http://example.com/2.jpg'}}
                },
                'contentDetails': {'duration': 'PT5M'},
                'statistics': {'viewCount': '3000', 'likeCount': '100', 'commentCount': '20'}
            }
        ]
    }

    with patch('app.scrapers.plugins.youtube_trending.build') as mock_build:
        # Mock YouTube client
        mock_youtube = MagicMock()
        mock_youtube.videos().list().execute.return_value = mock_api_response
        mock_build.return_value = mock_youtube

        # Create scraper
        scraper = YouTubeTrendingScraper(redis_client=redis_client)
        scraper.youtube = mock_youtube

        # Run scraper with keywords
        config = {'region_code': 'US', 'max_results': 50}
        keywords = ['python', 'blockchain', 'AI']

        results = await scraper.scrape(config, keywords)

        # Assertions
        assert len(results) == 1  # Only Python blockchain video matches
        assert results[0].video_id == 'vid1'
        assert results[0].title == 'Python Blockchain Tutorial'
        assert results[0].duration_seconds == 600
        assert results[0].view_count == 5000

        # Verify quota was recorded
        usage = await scraper.quota_manager.get_usage()
        assert usage == 100


@pytest.mark.asyncio
async def test_trending_scraping_with_quota_exhausted():
    """Test scraping behavior when quota is exhausted"""

    redis_client = FakeRedis(decode_responses=True)
    scraper = YouTubeTrendingScraper(redis_client=redis_client)

    # Exhaust quota
    await scraper.quota_manager.redis.set(
        scraper.quota_manager._get_quota_key(),
        10000  # At daily limit
    )

    # Attempt to scrape
    results = await scraper.scrape({'region_code': 'US'}, ['python'])

    # Should return empty list
    assert results == []
```

**Step 2: Run test to verify it passes**

Run: `pytest tests/test_integration/test_youtube_trending_flow.py -v`
Expected: PASS (2/2 tests)

**Step 3: Commit**

```bash
git add tests/test_integration/test_youtube_trending_flow.py
git commit -m "test(scrapers): add integration tests for trending scraper"
```

---

## Task 8: Add Celery Periodic Task

**Files:**
- Modify: `backend/app/tasks/celery_app.py:20-30` (beat_schedule section)
- Modify: `backend/app/tasks/scraping.py` (add new task)

**Step 1: Write test for Celery task**

Create `tests/test_tasks/test_youtube_trending_task.py`:

```python
import pytest
from unittest.mock import patch, AsyncMock, Mock
from app.tasks.scraping import scrape_youtube_trending


@pytest.mark.asyncio
async def test_scrape_youtube_trending_task():
    """Test Celery task for YouTube trending scraping"""

    with patch('app.tasks.scraping.get_scraper') as mock_get_scraper:
        with patch('app.tasks.scraping.get_db') as mock_get_db:
            # Mock scraper
            mock_scraper = Mock()
            mock_scraper.scrape = AsyncMock(return_value=[])
            mock_get_scraper.return_value = mock_scraper

            # Mock database
            mock_db = Mock()
            mock_get_db.return_value = mock_db

            # Mock keywords
            mock_db.query().filter().all.return_value = [
                Mock(keyword='python'),
                Mock(keyword='AI')
            ]

            # Run task
            result = await scrape_youtube_trending()

            # Verify scraper was called
            mock_scraper.scrape.assert_called_once()

            # Verify result
            assert 'status' in result
            assert result['status'] == 'success'
```

**Step 2: Implement Celery task**

Add to `backend/app/tasks/scraping.py`:

```python
from app.scrapers.factory import get_scraper
from app.database import get_db
from app.models.keyword import Keyword


@celery_app.task
async def scrape_youtube_trending():
    """
    Celery task: Scrape trending YouTube videos.
    Runs every 6 hours.
    """
    try:
        # Get active keywords
        db = next(get_db())
        keywords = db.query(Keyword).filter(Keyword.is_active == True).all()
        keyword_list = [kw.keyword for kw in keywords]

        # Get scraper
        scraper = get_scraper('youtube_trending')

        # Scrape with config
        config = {
            'region_code': 'US',
            'max_results': 50,
            'video_category': '28'  # Science & Technology
        }

        videos = await scraper.scrape(config, keyword_list)

        # Save to database (using existing storage layer)
        from app.scrapers.storage import save_articles
        saved_count = await save_articles(videos, db)

        logger.info(f"YouTube Trending: scraped {len(videos)}, saved {saved_count}")

        return {
            'status': 'success',
            'videos_scraped': len(videos),
            'videos_saved': saved_count
        }

    except Exception as e:
        logger.error(f"YouTube Trending scraping failed: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
```

**Step 3: Add to Celery beat schedule**

Update `backend/app/tasks/celery_app.py`:

```python
app.conf.beat_schedule = {
    # ... existing schedules ...

    'scrape-youtube-trending': {
        'task': 'app.tasks.scraping.scrape_youtube_trending',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
    },
}
```

**Step 4: Run test**

Run: `pytest tests/test_tasks/test_youtube_trending_task.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add app/tasks/scraping.py app/tasks/celery_app.py tests/test_tasks/test_youtube_trending_task.py
git commit -m "feat(tasks): add Celery task for YouTube trending scraping"
```

---

## Task 9: Manual End-to-End Verification

**Files:**
- None (manual testing)

**Step 1: Set YouTube API key**

Create `.env` file in `backend/`:

```bash
YOUTUBE_API_KEY=your_actual_api_key_here
```

**Step 2: Run scraper manually**

```bash
poetry run python -c "
import asyncio
from app.scrapers.factory import get_scraper
from fakeredis import FakeRedis

async def test():
    redis = FakeRedis(decode_responses=True)
    scraper = get_scraper('youtube_trending', redis_client=redis)

    config = {'region_code': 'US', 'max_results': 10}
    keywords = ['python', 'AI', 'machine learning']

    videos = await scraper.scrape(config, keywords)

    print(f'Scraped {len(videos)} videos')
    for v in videos[:3]:
        print(f'- {v.title} ({v.duration_seconds}s, {v.view_count} views)')

asyncio.run(test())
"
```

Expected output:
```
Scraped 5 videos
- Python Tutorial 2024 (600s, 50000 views)
- Machine Learning Basics (1200s, 120000 views)
- AI Ethics Discussion (900s, 30000 views)
```

**Step 3: Check quota usage**

```bash
poetry run python -c "
import asyncio
from app.youtube.quota_manager import YouTubeQuotaManager
from fakeredis import FakeRedis

async def check():
    redis = FakeRedis(decode_responses=True)
    manager = YouTubeQuotaManager(redis)
    usage = await manager.get_usage()
    print(f'Quota used: {usage}/10000')

asyncio.run(check())
"
```

Expected: Shows quota usage (should be 100)

**Step 4: Document verification**

No commit for this step - just verification

---

## Task 10: Update Documentation

**Files:**
- Modify: `backend/README.md` (if exists)
- Create: `docs/youtube-trending-scraper-usage.md`

**Step 1: Create usage documentation**

Create `docs/youtube-trending-scraper-usage.md`:

```markdown
# YouTube Trending Scraper - Usage Guide

## Overview

The YouTube Trending scraper fetches popular tech videos from YouTube's trending feed, filtered by user keywords.

## Configuration

### API Key

Set in `.env`:
```
YOUTUBE_API_KEY=your_youtube_api_key_here
```

Get API key: https://console.cloud.google.com/apis/credentials

### Scraper Config

```python
config = {
    'region_code': 'US',      # Geographic region
    'max_results': 50,         # Max videos per request (1-50)
    'video_category': '28'     # Science & Technology
}
```

## Scheduling

Runs automatically every 6 hours via Celery:
- 00:00, 06:00, 12:00, 18:00 UTC

## Quota Usage

- 100 units per scrape
- 400 units/day (4 scrapes)
- 8,000 units reserved for trending out of 10,000 daily quota

## Filtering

Videos filtered by active keywords from database:
- Matches in title, description, or tags
- Case-insensitive substring matching
- Minimum 1 keyword match required

## Manual Testing

```bash
cd backend
poetry run python -m app.scrapers.plugins.youtube_trending
```

## Monitoring

Check Celery logs for scraping results:
```bash
docker-compose logs -f celery
```

Logs show:
- Videos scraped
- Videos saved
- Quota usage
- Any errors
```

**Step 2: Commit documentation**

```bash
git add docs/youtube-trending-scraper-usage.md
git commit -m "docs: add YouTube Trending scraper usage guide"
```

---

## Verification Checklist

**Before marking complete:**

- [ ] All 25+ unit tests pass
- [ ] All 2 integration tests pass
- [ ] Manual API call works with real YouTube API
- [ ] Quota tracking works (Redis shows usage)
- [ ] Keyword filtering returns correct results
- [ ] Duration parsing handles all formats
- [ ] Error handling graceful (API errors, quota exhausted)
- [ ] Celery task registered in beat schedule
- [ ] Documentation complete and accurate

**Run full test suite:**

```bash
poetry run pytest tests/test_scrapers/test_youtube_trending.py tests/test_integration/test_youtube_trending_flow.py tests/test_tasks/test_youtube_trending_task.py -v --cov=app/scrapers/plugins/youtube_trending
```

Expected: 25+ tests passing, >90% coverage

---

## Success Criteria

✅ **Functional**
- Scraper fetches 30-50 trending tech videos per run
- Videos filtered by keywords (minimum 1 match)
- All metadata extracted correctly (title, duration, stats)
- ISO 8601 durations parsed to seconds
- Videos saved with `is_video=True`

✅ **Performance**
- API quota: ≤ 100 units per run
- Execution time: < 5 seconds
- No crashes on API failures

✅ **Testing**
- Unit tests: 20+ passing
- Integration tests: 2+ passing
- Coverage: > 90%

✅ **Integration**
- Celery task runs every 6 hours
- Quota manager prevents exhaustion
- Storage layer saves videos correctly

---

## Next Steps After Completion

1. Monitor Celery logs for first automated run
2. Verify videos appear in database with `is_video=True`
3. Check quota usage stays under 8,000/day
4. Consider adding:
   - Multiple region support
   - Video quality scoring
   - Engagement rate calculation
