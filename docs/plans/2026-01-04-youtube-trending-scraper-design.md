# YouTube Trending Scraper - Design Document

**Date**: 2026-01-04
**Status**: Design Complete - Ready for Implementation
**Author**: Design Session with User

## Overview

Complete the stub implementation of the YouTube Trending scraper to automatically fetch trending tech videos every 6 hours using YouTube Data API v3. This complements the RSS scraper (which tracks channel uploads) by discovering popular content the user might not be subscribed to.

## Purpose

Automatically discover trending technology content from YouTube that matches user interests, even from channels they haven't subscribed to. Provides a continuous stream of popular tech videos filtered by user keywords.

## Architecture

### High-Level Design

The scraper uses YouTube's `videos.list` API with the `chart=mostPopular` parameter, filtered by tech-related categories (Science & Technology = category 28). It integrates with the existing quota manager to ensure we stay within daily limits (8,000 units reserved for trending out of 10,000 total).

### Key Design Decisions

1. **API Strategy**: Use `videos.list` with `chart=mostPopular` + category filter (100 units per request, ~50 videos per call)
2. **Quota Management**: Check quota before each API call, record usage after
3. **Filtering**: Server-side category filter + client-side keyword matching against user's active keywords
4. **Caching**: 6-hour TTL to avoid redundant API calls
5. **Storage**: Save as `ScrapedYouTubeVideo` objects with `is_video=True`, deduplicate by video_id

## Data Flow & Components

### Component Structure

**YouTubeTrendingScraper** (`app/scrapers/plugins/youtube_trending.py`)
- Extends `ScraperPlugin` base class
- Uses existing `@scraper_plugin` decorator for auto-registration
- Accepts `config` dict with region code, max results, filtering options

### Workflow Steps

```
1. Check quota availability (via YouTubeQuotaManager)
   ↓
2. Call YouTube API: videos.list(
     chart='mostPopular',
     videoCategoryId='28',
     regionCode='US',
     maxResults=50
   )
   ↓
3. Record quota usage (100 units per call)
   ↓
4. Parse response → extract video metadata
   ↓
5. Filter by keywords (match against user's active keywords from DB)
   ↓
6. Convert to ScrapedYouTubeVideo objects
   ↓
7. Return to scraping task → saved to articles table
```

### Data Extracted Per Video

**From YouTube API Response:**
- `video_id` - Unique YouTube video identifier
- `title` - Video title
- `description` - Full video description
- `channel_id` - Channel identifier
- `channel_name` - Channel display name
- `thumbnail_url` - High-quality thumbnail (maxres or high)
- `duration` - ISO 8601 format (e.g., "PT4M13S")
- `view_count` - View count at scrape time
- `like_count` - Like count
- `comment_count` - Comment count
- `published_at` - Original publish timestamp
- `tags` - Video tags array

**Transformations:**
- Parse ISO 8601 duration → `duration_seconds` (integer)
- Extract thumbnail URL (prefer maxresdefault > high > medium)
- Set `is_video=True` automatically
- Set `source_type='youtube_trending'`

## Keyword Filtering & Configuration

### Multi-level Filtering Strategy

**1. Category Pre-filter** (Server-side)
- YouTube API parameter: `videoCategoryId='28'` (Science & Technology only)
- Reduces noise, ensures tech-related content
- No additional quota cost

**2. Keyword Matching** (Application-side)
- Load active keywords: `SELECT keyword, weight FROM keywords WHERE is_active = true`
- Match against: video title + description + tags
- Case-insensitive substring matching
- Score calculation: `sum(keyword.weight for matched keywords)`
- Minimum threshold: at least 1 keyword match (configurable)

**3. Deduplication**
- Query database: `SELECT id FROM articles WHERE video_id = ?`
- Skip videos already in database
- Prevents re-saving same trending video across multiple runs

### Configuration Options

**Scraper Config** (passed to `scrape()` method):

```python
{
    "region_code": "US",          # Geographic region for trending
    "max_results": 50,            # Videos per API call (max 50)
    "video_category": "28",       # Science & Technology
    "min_keyword_matches": 1,     # Minimum keywords required to match
    "include_shorts": False,      # Exclude YouTube Shorts (< 60 sec)
    "min_view_count": 1000        # Minimum views threshold
}
```

**Celery Beat Schedule:**

```python
# app/tasks/celery_app.py
'scrape-youtube-trending': {
    'task': 'app.tasks.scraping.scrape_youtube_trending',
    'schedule': crontab(hour='*/6'),  # Every 6 hours (00:00, 06:00, 12:00, 18:00)
}
```

**Estimated Quota Usage:**
- 100 units per scrape × 4 times/day = 400 units/day
- Well within 8,000 unit daily allocation for trending
- Leaves 7,600 units buffer for retries/errors

## Error Handling

### Quota Management

**Quota Exhausted:**
```python
if not await quota_manager.check_quota():
    logger.warning("YouTube API quota exhausted, skipping trending scrape")
    return []  # Return empty list gracefully
```

**Quota Warning:**
- At 95% usage (9,500/10,000): Log warning message
- At 100% usage: Skip scraping until next day (Redis TTL handles reset)

### API Errors

**Rate Limiting (429 Too Many Requests):**
- Exponential backoff: 2s, 4s (max 2 retries)
- If all retries fail: log error, return empty list
- Don't crash scraping task

**Forbidden (403):**
- Check API key validity
- Log error with context
- Return empty list

**Network Errors:**
- Timeout: 30 seconds per API call
- Connection errors: retry once after 2s delay
- Log all network errors

### Data Parsing Errors

**Malformed API Response:**
- Validate response structure before parsing
- Skip individual videos with missing required fields
- Continue processing remaining videos
- Log skipped videos with reason

**Duration Parsing:**
```python
try:
    duration_seconds = isodate.parse_duration(iso_duration).total_seconds()
except Exception as e:
    logger.warning(f"Failed to parse duration {iso_duration}: {e}")
    duration_seconds = None  # Optional field
```

## Testing Strategy

### Unit Tests

**File:** `tests/test_scrapers/test_youtube_trending.py`

**Test Cases:**

1. **Quota Checking:**
   - `test_trending_checks_quota_before_scrape()` - Verify quota check called
   - `test_trending_returns_empty_when_quota_exhausted()` - Graceful degradation

2. **API Interaction:**
   - `test_trending_calls_youtube_api_correctly()` - Verify API parameters
   - `test_trending_records_quota_usage()` - Verify usage tracking
   - `test_trending_handles_api_errors()` - 403, 429, network errors

3. **Data Parsing:**
   - `test_parse_trending_video()` - Valid video response
   - `test_parse_duration_iso8601()` - ISO duration parsing
   - `test_parse_handles_missing_optional_fields()` - Thumbnail, stats

4. **Keyword Filtering:**
   - `test_filter_by_keywords()` - Match in title/description/tags
   - `test_minimum_keyword_threshold()` - Reject videos with no matches
   - `test_exclude_shorts()` - Filter videos < 60 seconds

5. **Deduplication:**
   - `test_skip_existing_videos()` - Check database before saving
   - `test_deduplicate_by_video_id()` - Use video_id as unique key

### Integration Tests

**File:** `tests/test_integration/test_youtube_trending_flow.py`

**Test Cases:**

1. **End-to-End Flow:**
   - Mock YouTube API response with 10 trending videos
   - Load test keywords from database
   - Run scraper
   - Verify videos saved with `is_video=True`
   - Verify keyword matching worked correctly

2. **Quota Integration:**
   - Use fakeredis for quota manager
   - Verify quota recorded after scrape
   - Test quota exhaustion scenario

3. **Repeat Scraping:**
   - Run scraper twice with same data
   - Verify no duplicate videos created
   - Verify deduplication by video_id

## Integration Points

### Existing Systems

**1. YouTubeQuotaManager** (`app/youtube/quota_manager.py`)
- Already integrated in scraper stub ✓
- Uses Redis for distributed quota tracking
- Automatic daily reset via TTL

**2. ScraperPlugin Base Class** (`app/scrapers/base.py`)
- Extend `ScraperPlugin`
- Implement `async def scrape(config, keywords) -> List[ScrapedYouTubeVideo]`
- Auto-registered via `@scraper_plugin` decorator ✓

**3. Storage Layer** (`app/scrapers/storage.py`)
- Uses existing `save_articles()` function
- Accepts `ScrapedYouTubeVideo` objects (extends `ScrapedArticle`)
- Automatically handles `is_video=True` flag
- Deduplication by `external_id` (video_id)

**4. Celery Task Scheduler** (`app/tasks/celery_app.py`)
- Add new periodic task: `scrape_youtube_trending`
- Schedule: Every 6 hours via `crontab(hour='*/6')`

### New Dependencies

**Required:**
- `isodate` - ISO 8601 duration parsing (e.g., "PT4M13S" → 253 seconds)

**Already Installed:**
- `google-api-python-client` ✓
- `google-auth` ✓
- `redis` ✓

**Add to pyproject.toml:**
```toml
[tool.poetry.dependencies]
isodate = "^0.6.1"
```

### Database Schema

**No changes needed** - Uses existing tables:

- `articles` table with video fields (already added in YouTube integration) ✓
  - `video_id` (String 255)
  - `thumbnail_url` (Text)
  - `duration_seconds` (Integer)
  - `view_count` (Integer)
  - `is_video` (Boolean)

- `keywords` table for filtering (already exists) ✓

## Implementation Checklist

### Phase 1: Core Implementation
- [ ] Add `isodate` dependency to `pyproject.toml`
- [ ] Implement `_fetch_trending_videos()` method (YouTube API call)
- [ ] Implement `_parse_trending_video()` method (response parsing)
- [ ] Implement `_filter_by_keywords()` method (keyword matching)
- [ ] Implement main `scrape()` method (orchestration)
- [ ] Add ISO 8601 duration parsing with error handling

### Phase 2: Error Handling
- [ ] Add quota checking before API calls
- [ ] Add quota usage recording after API calls
- [ ] Implement exponential backoff for rate limits
- [ ] Handle API errors gracefully (403, 429, network)
- [ ] Add logging for all error cases

### Phase 3: Testing
- [ ] Write unit tests for API interaction (mocked)
- [ ] Write unit tests for data parsing
- [ ] Write unit tests for keyword filtering
- [ ] Write unit tests for error handling
- [ ] Write integration test for full scraping flow
- [ ] Verify all tests pass (target: 100% coverage)

### Phase 4: Integration
- [ ] Add Celery periodic task to beat schedule
- [ ] Verify scraper auto-registered via decorator
- [ ] Test quota manager integration with Redis
- [ ] Test storage integration (videos saved correctly)
- [ ] Manual end-to-end test with real API

### Phase 5: Verification
- [ ] Run scraper manually, verify API calls
- [ ] Check quota usage in Redis
- [ ] Verify videos saved to database with `is_video=True`
- [ ] Check deduplication works (run twice)
- [ ] Monitor Celery task execution

## Success Criteria

**Functional:**
- ✅ Scraper fetches 30-50 trending tech videos per run
- ✅ Videos filtered by user keywords (minimum 1 match)
- ✅ All video metadata extracted correctly
- ✅ ISO 8601 durations parsed to seconds
- ✅ Deduplication prevents duplicate saves
- ✅ Videos saved with `is_video=True` flag

**Performance:**
- ✅ API quota: ≤ 100 units per run (400 units/day)
- ✅ Execution time: < 5 seconds per scrape
- ✅ Error handling: No crashes on API failures

**Testing:**
- ✅ All unit tests pass (15+ tests)
- ✅ Integration tests pass (3+ tests)
- ✅ Test coverage: > 90%

## Future Enhancements

**Not in Scope (Future):**
- Multiple region support (currently US only)
- Custom category filtering (currently Science & Technology only)
- Video quality scoring (engagement rate, like ratio)
- ML-based trending prediction
- User feedback on trending recommendations

---

**Next Steps:**
1. Create implementation plan with detailed tasks
2. Set up isolated worktree for development
3. Follow TDD approach (test → implement → commit)
4. Code review before merging to main
