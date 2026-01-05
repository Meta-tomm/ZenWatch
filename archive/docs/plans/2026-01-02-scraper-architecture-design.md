# Scraper Architecture Design

**Date**: 2026-01-02
**Status**: Approved
**Author**: Design Session with Claude

## Overview

This document describes the base scraper architecture for TechWatch's multi-source scraping system. The design provides a robust, reusable foundation for scraping Reddit, HackerNews, Dev.to, GitHub Trending, Medium, and future sources.

## Design Goals

1. **Type Safety**: Pydantic validation catches data issues before database insertion
2. **Consistency**: Shared infrastructure (rate limiting, retries, caching) across all scrapers
3. **Resilience**: Smart retries with exponential backoff + jitter prevent API hammering
4. **Performance**: Redis caching reduces redundant API calls
5. **Maintainability**: Factory pattern enables easy addition of new scrapers
6. **Best Effort**: Individual article failures don't block entire scrapes

## Architecture Decisions

### 1. Return Type: Pydantic Models

**Decision**: Scrapers return `List[ScrapedArticle]` (Pydantic models)

**Rationale**:
- Type safety and validation catch errors early
- Separation of concerns - scrapers don't know about database schema
- Easy to test without database dependency
- Follows existing project patterns (Pydantic schemas already in use)

**Flow**: `Scraper → Pydantic (ScrapedArticle) → Service Layer → SQLAlchemy (Article) → Database`

### 2. Rate Limiting: Per-Scraper Configurable

**Decision**: Each scraper defines its own rate limits via class attributes

**Rationale**:
- Different APIs have different limits (Reddit: 60/min, HackerNews: 100/min)
- Respects each platform's constraints
- BaseScraper enforces limits automatically

**Implementation**: Semaphore + time-based throttling in `_rate_limited_request()`

### 3. Retry Strategy: Smart Exponential Backoff with Jitter

**Decision**: Automatic retries with exponential backoff + random jitter

**Retry Logic**:
- **429 (Rate Limit)**: Always retry with 2x backoff
- **500/502/503/504 (Server Errors)**: Retry with standard backoff
- **4xx (Client Errors)**: No retry, fail immediately
- **Network Errors**: Retry with backoff

**Jitter**: ±25% randomization prevents thundering herd problem

**Max Retries**: Configurable per scraper (default: 3)

### 4. Caching: Redis-Based with TTL

**Decision**: Cache raw responses in Redis with configurable TTL

**Rationale**:
- Redis already in stack (used by Celery)
- Shared cache across worker processes
- Reduces API calls during development/testing
- TTL prevents stale data

**Cache Key Format**: `scraper:{class_name}:{hash(keywords+max_results)}`

### 5. Configuration: Class Attributes

**Decision**: Scrapers define config as class constants

**Rationale**:
- Simple and explicit
- Version-controlled with code
- Easy to read and understand
- No external file parsing needed

**Example**:
```python
class RedditScraper(BaseScraper):
    RATE_LIMIT = 60
    CACHE_TTL = 3600
    MAX_RETRIES = 3
```

### 6. Error Handling: Best Effort

**Decision**: Skip invalid articles, log errors, return successes

**Rationale**:
- One bad article shouldn't block 99 good ones
- Production-friendly (resilient to partial failures)
- Errors logged for debugging
- Critical for scraping unreliable sources

## Component Design

### 1. ScrapedArticle Schema

**File**: `backend/app/schemas/scraped_article.py`

Pydantic model that all scrapers return:

```python
class ScrapedArticle(BaseModel):
    # Core fields (required)
    title: str
    url: HttpUrl
    source_type: str
    external_id: str

    # Content (optional)
    content: Optional[str]
    author: Optional[str]

    # Metadata
    published_at: datetime
    tags: List[str]
    upvotes: int
    comments_count: int

    # Source-specific data
    raw_data: dict
```

**Validation**:
- URL format validation
- Title length limits (1-500 chars)
- Content length limits (max 50k chars)
- Tag count limits (max 10)

### 2. BaseScraper Class

**File**: `backend/app/scrapers/base.py`

Abstract base class providing shared infrastructure:

**Key Methods**:
- `fetch_articles(keywords, max_results)` - Abstract method implemented by subclasses
- `fetch_with_cache(keywords, max_results)` - Public API with caching
- `_rate_limited_request(method, url, **kwargs)` - HTTP with rate limiting
- `_retry_request(method, url, **kwargs)` - Smart retry logic
- `_calculate_backoff(attempt, status_code)` - Exponential backoff + jitter
- `_get_cached(cache_key)` - Redis cache read
- `_set_cached(cache_key, data)` - Redis cache write
- `_make_cache_key(keywords, max_results)` - Cache key generation

**Configuration Attributes** (override in subclasses):
```python
RATE_LIMIT: int = 60        # requests per minute
CACHE_TTL: int = 3600       # cache duration in seconds
MAX_RETRIES: int = 3        # retry attempts
TIMEOUT: float = 30.0       # HTTP timeout
```

**Context Manager**: Supports `async with scraper:` pattern for proper HTTP client lifecycle

### 3. Rate Limiting Implementation

**Strategy**: Semaphore + time-based throttling

**Algorithm**:
1. Acquire semaphore slot (max concurrent = RATE_LIMIT)
2. Calculate time since last request
3. Sleep if needed to maintain minimum interval
4. Execute request
5. Update last request timestamp

**Minimum Interval**: `60 seconds / RATE_LIMIT`

**Example**: For RATE_LIMIT=60, minimum interval = 1 second between requests

### 4. Retry Logic with Jitter

**Exponential Backoff**:
- Attempt 0: 1s × jitter
- Attempt 1: 2s × jitter
- Attempt 2: 4s × jitter
- Attempt 3: 8s × jitter

**Jitter**: Random multiplier between 0.75 and 1.25

**Special Case**: 429 errors get 2x base delay

**Example Delays**:
- Normal retry: 1.2s, 2.3s, 3.8s, 9.1s
- Rate limit (429): 2.1s, 4.8s, 7.5s, 18.2s

### 5. Redis Caching

**Cache Key Format**: `scraper:{class_name}:{params_hash}`

**Workflow**:
1. Generate cache key from scraper class + params
2. Check Redis for cached data
3. If hit: deserialize and return
4. If miss: scrape fresh data
5. Cache results with TTL
6. Return fresh data

**Serialization**: JSON with datetime handling (`default=str`)

**TTL**: Configurable per scraper (default: 1 hour)

### 6. ScraperFactory Pattern

**File**: `backend/app/scrapers/factory.py`

Factory for dynamic scraper creation:

**Registration** (decorator):
```python
@ScraperFactory.register('hackernews')
class HackerNewsScraper(BaseScraper):
    ...
```

**Creation**:
```python
scraper = ScraperFactory.create('hackernews', redis_client)
```

**Methods**:
- `register(source_type)` - Decorator to register scrapers
- `create(source_type, redis_client)` - Create scraper instance
- `list_scrapers()` - Get all registered types
- `get_all_scrapers(redis_client)` - Create all scrapers at once

**Benefits**:
- Automatic scraper discovery
- No manual scraper mapping
- Easy to add new scrapers (just use decorator)
- Useful for "scrape all sources" tasks

## Example Implementation: HackerNews Scraper

**File**: `backend/app/scrapers/hackernews.py`

**Configuration**:
- Rate Limit: 100 req/min
- Cache TTL: 30 minutes
- Max Retries: 3

**Strategy**:
1. Fetch top 500 story IDs from Firebase API
2. Fetch each story's details individually
3. Filter by keywords in title
4. Parse and validate with Pydantic
5. Return up to `max_results` matching articles

**API**: HackerNews Firebase API (https://hacker-news.firebaseio.com/v0)

**Endpoints**:
- `/topstories.json` - List of top story IDs
- `/item/{id}.json` - Story details

**Error Handling**:
- Skip deleted stories
- Skip non-story items (jobs, polls)
- Log parsing errors but continue
- Return successful articles

## Usage in Celery Tasks

**File**: `backend/app/tasks/scraping.py`

**Task**: `scrape_all_sources()`

**Flow**:
1. Query active keywords from database
2. Initialize Redis client for caching
3. Get all scrapers via `ScraperFactory.get_all_scrapers()`
4. For each scraper:
   - Call `scraper.fetch_with_cache(keywords, max_results=50)`
   - Save articles to database with deduplication
   - Log results
   - Continue on errors (don't fail entire task)
5. Close Redis connection
6. Return total article count

**Deduplication**: Check if `article.url` already exists in database

**Schedule**: Runs every 6 hours via Celery Beat

## File Structure

```
backend/app/
├── schemas/
│   └── scraped_article.py      # Pydantic model
├── scrapers/
│   ├── __init__.py
│   ├── base.py                 # BaseScraper abstract class
│   ├── factory.py              # ScraperFactory pattern
│   ├── hackernews.py           # Example implementation
│   ├── reddit.py               # TODO
│   ├── devto.py                # TODO
│   ├── github.py               # TODO
│   └── medium.py               # TODO
└── tasks/
    └── scraping.py             # Celery tasks
```

## Testing Strategy

### Unit Tests

**Test BaseScraper**:
- Rate limiting enforcement
- Retry logic (mock failed requests)
- Backoff calculation with jitter
- Cache key generation

**Test Individual Scrapers**:
- Mock HTTP responses
- Validate Pydantic parsing
- Test keyword filtering
- Error handling (invalid data)

**Test ScraperFactory**:
- Registration decorator
- Scraper creation
- Unknown type handling

### Integration Tests

**Test with Live APIs** (limited):
- Fetch small batch (5-10 articles)
- Verify Pydantic validation
- Check database insertion
- Test end-to-end flow

**Use VCR.py**: Record/replay HTTP responses for deterministic tests

## Performance Considerations

**Expected Throughput**:
- HackerNews (100 req/min): ~100 articles in 5 minutes
- Reddit (60 req/min): ~60 articles in 1 minute
- Dev.to (unlimited): ~100 articles in <1 minute

**Bottlenecks**:
- API rate limits (primary constraint)
- Network latency (secondary)
- Database writes (minimal - batch possible)

**Optimization**:
- Redis caching reduces redundant scrapes
- Parallel scraping (multiple Celery workers)
- Batch database inserts (future enhancement)

## Security Considerations

**API Keys**:
- Store in environment variables (`.env`)
- Never commit to repository
- Use separate keys for dev/prod

**User Agents**:
- Identify as "TechWatch/1.0 (Educational Project)"
- Include contact info if scraping at scale

**Rate Limiting**:
- Respect platform TOS
- Conservative limits to avoid bans
- Exponential backoff on 429 errors

**Data Validation**:
- Pydantic prevents malformed data
- URL validation prevents injection
- Content length limits prevent memory issues

## Future Enhancements

### Short Term
1. Implement Reddit scraper (OAuth2)
2. Implement Dev.to scraper (REST API)
3. Implement GitHub Trending scraper (HTML parsing)
4. Implement Medium scraper (RSS)
5. Add comprehensive tests

### Medium Term
1. Prometheus metrics (scrape duration, error rates, cache hit rate)
2. Dead letter queue for failed scrapes
3. Scraper health checks
4. Admin UI for scraper status

### Long Term
1. Adaptive rate limiting (detect and respect 429 headers)
2. Distributed scraping (multiple workers, coordinated rate limiting)
3. Machine learning for optimal scrape scheduling
4. WebSocket support for real-time sources

## Dependencies

**New**:
- `httpx` - Async HTTP client
- `redis[asyncio]` - Redis client with async support
- `beautifulsoup4` - HTML parsing (for GitHub, Medium)
- `lxml` - Fast XML/HTML parser

**Existing**:
- `pydantic` - Data validation
- `celery` - Task queue
- `sqlalchemy` - ORM

## Success Metrics

**Technical**:
- Scrape 100+ articles per day per source
- Cache hit rate >30%
- Error rate <5%
- API rate limit violations = 0

**Business**:
- Article freshness <6 hours
- Keyword match accuracy >80%
- Zero downtime scraping

## Rollout Plan

1. **Week 1**: Implement base architecture + HackerNews scraper
2. **Week 2**: Add Reddit + Dev.to scrapers
3. **Week 3**: Add GitHub + Medium scrapers
4. **Week 4**: Testing, monitoring, optimization

## References

- [HackerNews API Docs](https://github.com/HackerNews/API)
- [Reddit API Docs](https://www.reddit.com/dev/api)
- [Dev.to API Docs](https://developers.forem.com/api)
- [httpx Documentation](https://www.python-httpx.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Next Steps**: Ready to implement? Use superpowers:writing-plans to create detailed implementation plan.
