# YouTube Trending Scraper - Usage Guide

## Overview

The YouTube Trending scraper fetches popular tech videos from YouTube's trending feed, filtered by user keywords. It uses the YouTube Data API v3 to retrieve trending videos in the Science & Technology category.

## Configuration

### API Key

Set in `.env`:

```bash
YOUTUBE_API_KEY=your_youtube_api_key_here
```

Get an API key from: https://console.cloud.google.com/apis/credentials

### Scraper Config

```python
config = {
    "region_code": "US",           # Geographic region (ISO 3166-1 alpha-2)
    "max_results": 50,             # Max videos per request (1-50)
    "video_category": "28",        # 28 = Science & Technology
    "min_keyword_matches": 1,      # Minimum keyword matches required
    "include_shorts": True,        # Include YouTube Shorts (<60s)
    "min_view_count": 0            # Minimum view count threshold
}
```

### Keyword Structure

Keywords are stored in the database with weights for relevance scoring:

```python
keywords = [
    {"keyword": "rust", "weight": 5.0, "category": "programming"},
    {"keyword": "python", "weight": 4.0, "category": "programming"},
    {"keyword": "machine learning", "weight": 3.0, "category": "ai"}
]
```

## Scheduling

The scraper runs automatically via Celery Beat:

- **Schedule:** Every 6 hours (00:00, 06:00, 12:00, 18:00 UTC)
- **Task name:** `scrape_youtube_trending`

### Manual Trigger

```python
from app.tasks.scraping import scrape_youtube_trending

# Trigger immediately
result = scrape_youtube_trending.delay()

# With custom config
result = scrape_youtube_trending.delay({
    "region_code": "GB",
    "max_results": 25
})
```

## Quota Usage

YouTube Data API v3 has a daily quota of 10,000 units.

| Operation | Units |
|-----------|-------|
| videos.list (trending) | 100 |

**Daily quota budget:**
- 4 scrapes/day at 100 units = 400 units
- Reserved for trending: ~8,000 units/day
- Remaining for other operations: ~2,000 units/day

The scraper uses `YouTubeQuotaManager` to track and limit API usage.

## Filtering

Videos are filtered by matching active keywords from the database:

1. **Text matching:** Keywords are matched against title + description + tags (case-insensitive)
2. **Scoring:** Each matched keyword adds its weight to the relevance score
3. **Threshold:** Videos must match at least `min_keyword_matches` keywords
4. **Additional filters:**
   - `include_shorts=False`: Exclude videos under 60 seconds
   - `min_view_count=1000`: Exclude videos with fewer views

## Output

Each scraped video is returned as a `ScrapedYouTubeVideo` object:

```python
{
    "video_id": "abc123",
    "title": "Building AI Apps with Python",
    "url": "https://www.youtube.com/watch?v=abc123",
    "source_type": "youtube_trending",
    "channel_id": "UCxxx",
    "channel_name": "Tech Channel",
    "description": "...",
    "thumbnail_url": "https://i.ytimg.com/...",
    "duration_seconds": 600,
    "view_count": 50000,
    "tags": ["python", "ai", "tutorial"],
    "published_at": "2024-01-01T10:00:00Z",
    "score": 9.0  # Relevance score based on matched keywords
}
```

## Monitoring

### Check Celery Logs

```bash
docker-compose logs -f celery
```

Logs show:
- Videos scraped count
- Videos saved count
- Quota usage
- Any errors

### Database Queries

```sql
-- Recent trending videos
SELECT title, view_count, score
FROM articles
WHERE source_type = 'youtube_trending'
ORDER BY created_at DESC
LIMIT 10;

-- Scraping run history
SELECT task_id, status, articles_scraped, articles_saved, created_at
FROM scraping_runs
WHERE source_type = 'youtube_trending'
ORDER BY created_at DESC
LIMIT 5;
```

## Error Handling

The scraper handles errors gracefully:

| Error | Behavior |
|-------|----------|
| Quota exhausted | Returns empty list, logs warning |
| API 403 Forbidden | Returns empty list, logs error |
| API 429 Rate Limit | Retries with exponential backoff (2s, 4s) |
| Network error | Returns empty list, logs error |
| No active keywords | Skips scraping, logs warning |

## Testing

Run the test suite:

```bash
# Unit tests
poetry run pytest tests/test_scrapers/test_youtube_trending.py -v

# Integration tests
poetry run pytest tests/test_integration/test_youtube_trending_flow.py -v

# Celery task tests
poetry run pytest tests/test_tasks/test_youtube_trending_task.py -v

# All YouTube Trending tests
poetry run pytest tests/test_scrapers/test_youtube_trending.py tests/test_integration/test_youtube_trending_flow.py tests/test_tasks/test_youtube_trending_task.py -v
```

Expected: 25+ tests passing

## Architecture

```
app/scrapers/plugins/youtube_trending.py  # Main scraper implementation
app/tasks/scraping.py                      # Celery task wrapper
app/tasks/celery_app.py                    # Beat schedule config
app/youtube/quota_manager.py               # Quota tracking
app/schemas/scraped_article.py             # ScrapedYouTubeVideo schema
```

## Troubleshooting

### No videos returned

1. Check API key is set in `.env`
2. Verify active keywords exist in database
3. Check quota hasn't been exhausted
4. Try increasing `max_results` or adjusting keywords

### Quota errors

1. Check Redis for current usage: `GET youtube_quota:YYYY-MM-DD`
2. Wait for quota reset (midnight Pacific Time)
3. Consider reducing scrape frequency

### Celery task not running

1. Verify Celery worker is running
2. Check beat schedule in `celery_app.py`
3. Restart Celery: `docker-compose restart celery`
