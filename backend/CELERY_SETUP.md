# Celery Setup Guide

## Overview

TechWatch uses Celery for asynchronous task processing and scheduled scraping jobs.

## Components

1. **Celery Worker** - Executes scraping tasks
2. **Celery Beat** - Scheduler for periodic tasks
3. **Redis** - Message broker and result backend

## Starting Services

### 1. Start Redis (required)

```bash
# Using Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or using docker-compose
docker-compose up -d redis
```

### 2. Start Celery Worker

```bash
cd backend
poetry run celery -A app.tasks.celery_app worker --loglevel=info
```

**Options:**
- `--loglevel=debug` - More verbose logging
- `--concurrency=4` - Number of worker processes (default: CPU count)
- `--pool=solo` - Single process (useful for debugging)

### 3. Start Celery Beat (Scheduler)

```bash
cd backend
poetry run celery -A app.tasks.celery_app beat --loglevel=info
```

**Note:** Only run ONE beat instance. Multiple beat instances will cause duplicate tasks.

### 4. Combined Worker + Beat (Development only)

```bash
cd backend
poetry run celery -A app.tasks.celery_app worker --beat --loglevel=info
```

## Scheduled Tasks

### Configured Schedules

1. **Every 6 Hours** (00:00, 06:00, 12:00, 18:00 UTC)
   - Task: `scrape_all_sources`
   - Keywords: Default (python, AI, machine learning, blockchain)
   - Purpose: Regular automated scraping

2. **Daily at 08:00 UTC**
   - Task: `scrape_all_sources`
   - Keywords: Custom (python, AI, blockchain, kubernetes, rust)
   - Purpose: Morning digest preparation
   - Expires: After 1 hour if not executed

## Manual Task Triggering

### Via Python

```python
from app.tasks.scraping import scrape_all_sources

# Trigger immediate execution
result = scrape_all_sources.delay(keywords=["python", "AI"])
print(f"Task ID: {result.id}")

# Check task status
print(result.status)  # PENDING, STARTED, SUCCESS, FAILURE
```

### Via API

```bash
# Trigger scraping via REST API
curl -X POST http://localhost:8000/api/scraping/trigger \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["python", "AI"]}'

# Get task status
curl http://localhost:8000/api/scraping/status/{task_id}
```

## Monitoring

### Flower (Web UI)

Install and run Flower for monitoring:

```bash
poetry add flower
poetry run celery -A app.tasks.celery_app flower --port=5555
```

Access at: http://localhost:5555

### Command Line

```bash
# List active tasks
poetry run celery -A app.tasks.celery_app inspect active

# List scheduled tasks
poetry run celery -A app.tasks.celery_app inspect scheduled

# List registered tasks
poetry run celery -A app.tasks.celery_app inspect registered

# Worker stats
poetry run celery -A app.tasks.celery_app inspect stats
```

## Production Deployment

### Systemd Service (Linux)

**celery-worker.service:**
```ini
[Unit]
Description=Celery Worker
After=network.target redis.target

[Service]
Type=forking
User=techwatch
Group=techwatch
WorkingDirectory=/app/backend
Environment="PATH=/app/backend/.venv/bin"
ExecStart=/app/backend/.venv/bin/celery -A app.tasks.celery_app worker \
  --loglevel=info \
  --pidfile=/var/run/celery/worker.pid \
  --logfile=/var/log/celery/worker.log

[Install]
WantedBy=multi-user.target
```

**celery-beat.service:**
```ini
[Unit]
Description=Celery Beat
After=network.target redis.target

[Service]
Type=simple
User=techwatch
Group=techwatch
WorkingDirectory=/app/backend
Environment="PATH=/app/backend/.venv/bin"
ExecStart=/app/backend/.venv/bin/celery -A app.tasks.celery_app beat \
  --loglevel=info \
  --pidfile=/var/run/celery/beat.pid \
  --logfile=/var/log/celery/beat.log \
  --schedule=/var/run/celery/celerybeat-schedule

[Install]
WantedBy=multi-user.target
```

### Docker Compose

Already configured in `docker-compose.yml`:

```yaml
celery_worker:
  build: ./backend
  command: celery -A app.tasks.celery_app worker --loglevel=info
  depends_on:
    - redis
    - postgres

celery_beat:
  build: ./backend
  command: celery -A app.tasks.celery_app beat --loglevel=info
  depends_on:
    - redis
    - postgres
```

## Troubleshooting

### Worker not starting
- Check Redis is running: `redis-cli ping` (should return PONG)
- Check DATABASE_URL and REDIS_URL in .env
- Check logs: `--loglevel=debug`

### Tasks not executing
- Verify worker is running and consuming from queue
- Check task is registered: `celery -A app.tasks.celery_app inspect registered`
- Check Redis connection

### Beat not scheduling
- Only one beat instance should run
- Check beat logs for schedule registration
- Verify timezone settings (UTC)

### Task stuck in PENDING
- Worker might be down
- Task might have wrong name
- Check worker logs for errors

## Configuration

Edit schedules in `app/tasks/celery_app.py`:

```python
celery_app.conf.beat_schedule = {
    'my-custom-task': {
        'task': 'scrape_all_sources',
        'schedule': crontab(hour=12, minute=0),  # Daily at noon
        'kwargs': {'keywords': ['custom', 'keywords']},
    },
}
```

### Crontab Schedule Examples

```python
from celery.schedules import crontab

# Every minute
crontab()

# Every 15 minutes
crontab(minute='*/15')

# Every hour
crontab(minute=0)

# Every 6 hours
crontab(hour='*/6')

# Daily at 08:00
crontab(hour=8, minute=0)

# Weekdays at 09:00
crontab(hour=9, minute=0, day_of_week='1-5')

# First day of month at 00:00
crontab(hour=0, minute=0, day_of_month=1)
```

## Best Practices

1. **Always run Beat as a singleton** - Multiple beat instances cause duplicate tasks
2. **Use task expiration** - Set `expires` for time-sensitive tasks
3. **Monitor task execution** - Use Flower or logging
4. **Handle failures gracefully** - Tasks should be idempotent
5. **Set appropriate timeouts** - Prevent hung tasks
6. **Scale workers horizontally** - Add more workers for high load
7. **Use task routing** - Route different tasks to different queues/workers
