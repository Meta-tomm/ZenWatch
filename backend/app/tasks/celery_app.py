from celery import Celery
from celery.schedules import crontab
from app.config import settings

# Create Celery app
celery_app = Celery(
    'techwatch',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        'app.tasks.scraping',
        'app.tasks.scoring',
        'app.tasks.trends'
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Celery Beat schedule - Automated periodic tasks
celery_app.conf.beat_schedule = {
    'scrape-all-sources-every-6-hours': {
        'task': 'scrape_all_sources',
        'schedule': crontab(hour='*/6'),  # Every 6 hours: 00:00, 06:00, 12:00, 18:00
        'kwargs': {
            'keywords': None  # Use default keywords from task
        },
    },
    'scrape-all-sources-daily-morning': {
        'task': 'scrape_all_sources',
        'schedule': crontab(hour=8, minute=0),  # Every day at 08:00
        'kwargs': {
            'keywords': ['python', 'AI', 'blockchain', 'kubernetes', 'rust']
        },
        'options': {
            'expires': 3600,  # Task expires after 1 hour if not executed
        }
    },
    'score-new-articles-hourly': {
        'task': 'score_articles',
        'schedule': crontab(minute=15),  # Every hour at :15 (after scraping)
        'kwargs': {
            'article_ids': None  # Score all unscored articles
        },
    },
    'summarize-new-articles-daily': {
        'task': 'summarize_articles',
        'schedule': crontab(hour=9, minute=0),  # Daily at 09:00
        'kwargs': {
            'article_ids': None  # Summarize all articles without summaries
        },
        'options': {
            'expires': 7200,  # Task expires after 2 hours
        }
    },
    'detect-trends-daily': {
        'task': 'detect_trends',
        'schedule': crontab(hour=10, minute=0),  # Daily at 10:00 (after scoring)
    },
    'cleanup-old-trends-weekly': {
        'task': 'cleanup_old_trends',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Sundays at 03:00
        'kwargs': {
            'days_to_keep': 90  # Keep 90 days of trends
        },
    },
}
