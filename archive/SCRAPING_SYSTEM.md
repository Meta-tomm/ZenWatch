# TechWatch Scraping System Documentation

## Overview

The TechWatch scraping system is a modular, scalable platform for collecting tech articles from multiple sources (Reddit, HackerNews, etc.). It uses a plugin architecture for extensibility and Celery for distributed task execution.

## Architecture

### Core Components

1. **Plugin System** (`app/scrapers/`)
   - `base.py`: Abstract base class for all scrapers
   - `registry.py`: Singleton registry with decorator-based auto-discovery
   - `plugins/`: Scraper implementations (reddit.py, hackernews.py)
   - `strategies/`: Rate limiting and retry logic

2. **Storage Layer** (`app/scrapers/storage.py`)
   - Handles article persistence with deduplication
   - Updates existing articles instead of creating duplicates

3. **Task Orchestration** (`app/tasks/scraping.py`)
   - Celery tasks for async execution
   - Scrapes all active sources in parallel
   - Tracks execution in `scraping_runs` table

4. **API** (`app/api/scraping.py`)
   - `POST /api/scraping/trigger`: Trigger manual scraping
   - `GET /api/scraping/status/{task_id}`: Check scraping status

5. **Scheduler** (Celery Beat)
   - Configured in `app/tasks/celery_app.py`
   - Runs every 6 hours automatically

### Data Flow

```
Celery Beat (Every 6h)
  │
  ├─> scrape_all_sources task
  │     │
  │     ├─> Fetch active sources from DB
  │     │
  │     ├─> For each source:
  │     │     ├─> Get scraper from registry
  │     │     ├─> Validate config
  │     │     ├─> Scrape articles (with rate limiting)
  │     │     ├─> Filter by keywords
  │     │     └─> Save to database
  │     │
  │     └─> Record results in scraping_runs
  │
  └─> Articles stored in database
```

## Plugin Development

### Creating a New Scraper

1. **Create plugin file** in `app/scrapers/plugins/your_scraper.py`:

```python
from typing import List, Dict
from datetime import datetime
import httpx
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.scrapers.strategies.rate_limit import RateLimiter

@scraper_plugin(
    name="your_scraper",  # Unique identifier
    display_name="Your Scraper",  # Human-readable name
    version="1.0.0"
)
class YourScraper(ScraperPlugin):

    def __init__(self):
        super().__init__()
        self.rate_limiter = RateLimiter(requests_per_minute=60)

    def validate_config(self, config: Dict) -> bool:
        """Validate scraper configuration"""
        required_fields = ['api_key', 'endpoint']
        return all(field in config for field in required_fields)

    async def scrape(self, config: Dict, keywords: List[str]) -> List[Dict]:
        """
        Scrape articles from your source

        Returns:
            List of article dictionaries with fields:
            - title (required)
            - url (required)
            - external_id (optional): Source's article ID
            - published_at (optional): datetime
            - author (optional)
            - content (optional)
            - upvotes (optional)
            - comments_count (optional)
            - tags (optional): List[str]
        """
        articles = []

        async with self.rate_limiter:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    config['endpoint'],
                    headers={'Authorization': f"Bearer {config['api_key']}"}
                )
                response.raise_for_status()

                for item in response.json()['items']:
                    # Filter by keywords
                    if await self._quick_match(item['title'], keywords):
                        articles.append({
                            'title': item['title'],
                            'url': item['url'],
                            'external_id': item['id'],
                            'published_at': datetime.fromisoformat(item['date']),
                            'author': item.get('author', 'unknown'),
                            'content': item.get('content', ''),
                            'tags': item.get('tags', [])
                        })

        return articles
```

2. **Auto-registration**: Plugin is automatically registered when imported via the `@scraper_plugin` decorator

3. **Test your plugin**:

```python
# tests/test_scrapers/test_your_scraper.py
import pytest
from app.scrapers.plugins.your_scraper import YourScraper

@pytest.mark.asyncio
async def test_your_scraper():
    scraper = YourScraper()
    config = {'api_key': 'test', 'endpoint': 'https://api.example.com'}

    assert scraper.validate_config(config)

    articles = await scraper.scrape(config, keywords=['python'])
    assert isinstance(articles, list)
```

### Plugin Best Practices

- **Rate Limiting**: Always use `RateLimiter` to respect API limits
- **Error Handling**: Let exceptions bubble up - the orchestrator handles retries
- **Keyword Filtering**: Use `await self._quick_match(title, keywords)` for basic filtering
- **Deduplication**: Return consistent URLs - storage layer handles dedup automatically
- **Config Validation**: Validate all required config fields in `validate_config()`

## Database Schema

### Sources Table

```sql
CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    type VARCHAR(50) NOT NULL,
    base_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    scrape_frequency_hours INTEGER DEFAULT 6,
    last_scraped_at TIMESTAMP,
    config JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**Config Examples:**

- **HackerNews**: `{"max_articles": 50, "story_type": "top"}`
- **Reddit**: `{"client_id": "xxx", "client_secret": "yyy", "subreddits": ["python"], "max_articles": 50}`

### Articles Table

```sql
CREATE TABLE articles (
    id SERIAL PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    external_id VARCHAR(255),
    source_type VARCHAR(50) NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    content TEXT,
    summary TEXT,
    author VARCHAR(255),
    published_at TIMESTAMP,
    scraped_at TIMESTAMP DEFAULT NOW(),
    score FLOAT,
    category VARCHAR(100),
    tags TEXT[],  -- Array in PostgreSQL, JSON in SQLite
    language VARCHAR(10) DEFAULT 'en',
    read_time_minutes INTEGER,
    upvotes INTEGER,
    comments_count INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    is_favorite BOOLEAN DEFAULT FALSE,
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_articles_url ON articles(url);
CREATE INDEX idx_articles_score ON articles(score DESC);
```

### Scraping Runs Table

```sql
CREATE TABLE scraping_runs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL UNIQUE,
    source_type VARCHAR(50),
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    articles_scraped INTEGER DEFAULT 0,
    articles_saved INTEGER DEFAULT 0,
    error_message TEXT
);
```

## API Usage

### Trigger Scraping

```bash
curl -X POST http://localhost:8000/api/scraping/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["python", "AI", "blockchain"]
  }'
```

**Response:**
```json
{
  "status": "accepted",
  "message": "Scraping task started",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

### Check Status

```bash
curl http://localhost:8000/api/scraping/status/{task_id}
```

**Response:**
```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "success",
  "started_at": "2025-12-30T20:00:00Z",
  "completed_at": "2025-12-30T20:02:15Z",
  "articles_scraped": 47,
  "articles_saved": 45,
  "error_message": null
}
```

**Status values:**
- `running`: Scraping in progress
- `success`: Completed successfully (no errors)
- `partial_success`: Completed with some source failures
- `failed`: All sources failed

## Deployment

### Prerequisites

- Python 3.11+
- PostgreSQL 16+
- Redis 7+
- Poetry (dependency management)

### Setup Steps

1. **Install dependencies:**
```bash
cd backend
poetry install
```

2. **Configure environment** (`.env`):
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/techwatch
REDIS_URL=redis://localhost:6379/0
ANTHROPIC_API_KEY=your_api_key_here
SECRET_KEY=your_secret_key_here
```

3. **Run migrations:**
```bash
poetry run alembic upgrade head
```

4. **Seed initial sources:**
```bash
poetry run python -m app.scripts.seed_sources
```

5. **Start services:**

**Terminal 1 - API:**
```bash
poetry run uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Celery Worker:**
```bash
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

**Terminal 3 - Celery Beat (Scheduler):**
```bash
poetry run celery -A app.tasks.celery_app beat --loglevel=info
```

### Docker Deployment

See `../docker-compose.yml` for complete setup.

```bash
# From project root
docker-compose up -d
```

This starts:
- PostgreSQL database
- Redis
- FastAPI backend
- Celery worker
- Celery beat scheduler

## Configuration

### Celery Beat Schedule

Edit `app/tasks/celery_app.py` to modify scraping schedule:

```python
celery_app.conf.beat_schedule = {
    'scrape-every-6-hours': {
        'task': 'scrape_all_sources',
        'schedule': crontab(hour='*/6'),  # Every 6 hours
        'kwargs': {'keywords': None}  # Use default keywords
    },
    'scrape-daily-morning': {
        'task': 'scrape_all_sources',
        'schedule': crontab(hour=8, minute=0),  # Daily at 08:00 UTC
        'kwargs': {
            'keywords': ['python', 'AI', 'blockchain']
        }
    }
}
```

### Rate Limiting

Configured per-scraper in plugin `__init__()`:

```python
self.rate_limiter = RateLimiter(requests_per_minute=60)
```

### Retry Strategy

Configured in plugin initialization:

```python
from app.scrapers.strategies.retry import RetryStrategy

self.retry_strategy = RetryStrategy(
    max_retries=3,
    backoff_factor=2.0
)

# Use in scrape method:
articles = await self.retry_strategy.execute(
    lambda: self._fetch_articles(config)
)
```

## Troubleshooting

### No articles scraped

**Symptoms:** `articles_scraped: 0` in scraping run

**Possible causes:**
1. Keywords don't match any article titles
2. Source is inactive (`is_active=false`)
3. Rate limiting too aggressive
4. API credentials invalid

**Solutions:**
- Check source config in database
- Verify keywords are present in article titles
- Check scraper logs for errors
- Test scraper directly: `poetry run pytest tests/test_scrapers/`

### Celery tasks not executing

**Symptoms:** Task status stuck in PENDING

**Possible causes:**
1. Worker not running
2. Redis connection failed
3. Task name mismatch

**Solutions:**
```bash
# Check worker status
poetry run celery -A app.tasks.celery_app inspect active

# Check registered tasks
poetry run celery -A app.tasks.celery_app inspect registered

# Restart worker
pkill -f "celery worker"
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

### Database migration errors

**Symptoms:** `alembic upgrade head` fails

**Solutions:**
```bash
# Reset migrations (CAUTION: destroys data)
poetry run alembic downgrade base
poetry run alembic upgrade head

# Or manually create tables
poetry run python -c "from app.database import Base, engine; Base.metadata.create_all(engine)"
```

### Duplicate articles

**Symptoms:** Same article appears multiple times

**Cause:** URL not consistent between scrapes

**Solution:** Ensure scraper returns canonical URLs:
```python
# Bad
url = "https://reddit.com/r/python/comments/abc123"

# Good
url = "https://reddit.com/r/python/comments/abc123/title-slug"
```

### Memory leaks in Celery workers

**Symptoms:** Worker memory grows over time

**Solution:** Restart workers periodically:
```python
# celery_app.py
celery_app.conf.worker_max_tasks_per_child = 1000  # Restart after 1000 tasks
```

## Monitoring

### Logs

```bash
# Application logs
tail -f logs/app.log

# Celery worker logs
tail -f logs/celery_worker.log

# Celery beat logs
tail -f logs/celery_beat.log
```

### Metrics

Key metrics to track:
- Articles scraped per hour
- Source failure rate
- Average scraping duration
- Queue depth (Celery)
- Worker utilization

Query scraping history:
```sql
SELECT
    DATE(started_at) as date,
    COUNT(*) as runs,
    SUM(articles_scraped) as total_articles,
    AVG(articles_scraped) as avg_per_run,
    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failures
FROM scraping_runs
WHERE started_at > NOW() - INTERVAL '7 days'
GROUP BY DATE(started_at)
ORDER BY date DESC;
```

## Testing

### Run all tests

```bash
poetry run pytest
```

### Test specific component

```bash
# Scrapers
poetry run pytest tests/test_scrapers/

# Integration tests
poetry run pytest tests/test_integration/

# With coverage
poetry run pytest --cov=app tests/
```

### Test individual scraper

```python
import asyncio
from app.scrapers.plugins.hackernews import HackerNewsScraper

async def test():
    scraper = HackerNewsScraper()
    config = {'max_articles': 5, 'story_type': 'top'}
    articles = await scraper.scrape(config, keywords=['python'])
    print(f"Found {len(articles)} articles")
    for article in articles:
        print(f"  - {article['title']}")

asyncio.run(test())
```

## Performance Optimization

### Database Indexes

Already created:
- `idx_articles_url` (for deduplication)
- `idx_articles_score` (for ranking)

Add custom indexes as needed:
```sql
CREATE INDEX idx_articles_category ON articles(category);
CREATE INDEX idx_articles_published ON articles(published_at DESC);
```

### Celery Concurrency

Adjust worker concurrency based on workload:
```bash
# 4 concurrent tasks
poetry run celery -A app.tasks.celery_app worker --concurrency=4

# Auto-scale: 2-10 workers
poetry run celery -A app.tasks.celery_app worker --autoscale=10,2
```

### Caching

Add Redis caching for frequently accessed data:
```python
from app.cache import cache

@cache.memoize(timeout=300)  # 5 minutes
def get_active_sources():
    return db.query(Source).filter_by(is_active=True).all()
```

## Security

### API Security

- Rate limiting: 100 requests/minute per IP
- Authentication: Required for write operations
- CORS: Configured for frontend origin only

### Secrets Management

- Never commit `.env` files
- Use environment variables in production
- Rotate API keys regularly
- Use minimal privilege database users

### Input Validation

- All API inputs validated with Pydantic
- SQL injection prevented via SQLAlchemy ORM
- URL validation for external sources

## Support & Contributing

### Reporting Issues

Include:
- Error messages and stack traces
- Scraper logs
- Database query results
- Environment (OS, Python version, dependencies)

### Adding New Sources

1. Fork repository
2. Create plugin following development guide
3. Add comprehensive tests
4. Update documentation
5. Submit pull request

## License

See LICENSE file in project root.

## Changelog

### v1.0.0 (2025-12-30)
- Initial release
- HackerNews and Reddit scrapers
- Plugin architecture
- Celery-based orchestration
- REST API
- Comprehensive test suite (46 tests)
