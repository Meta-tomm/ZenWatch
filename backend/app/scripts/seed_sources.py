"""
Seed initial sources into the database

This script populates the database with pre-configured sources
for HackerNews and Reddit scraping.

Usage:
    python -m app.scripts.seed_sources
    # or
    poetry run python -m app.scripts.seed_sources
"""

from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app.models.source import Source
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Initial sources configuration
INITIAL_SOURCES = [
    {
        "name": "HackerNews",
        "type": "hackernews",
        "base_url": "https://hacker-news.firebaseio.com/v0",
        "is_active": True,
        "scrape_frequency_hours": 6,
        "config": {
            "max_articles": 50,
            "story_type": "top"
        }
    },
    {
        "name": "Reddit - Programming",
        "type": "reddit",
        "base_url": "https://oauth.reddit.com",
        "is_active": True,
        "scrape_frequency_hours": 6,
        "config": {
            "client_id": "YOUR_REDDIT_CLIENT_ID",
            "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
            "subreddits": ["programming", "python", "javascript", "webdev"],
            "max_articles": 50
        }
    },
    {
        "name": "Reddit - AI/ML",
        "type": "reddit",
        "base_url": "https://oauth.reddit.com",
        "is_active": True,
        "scrape_frequency_hours": 6,
        "config": {
            "client_id": "YOUR_REDDIT_CLIENT_ID",
            "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
            "subreddits": ["MachineLearning", "artificial", "deeplearning"],
            "max_articles": 30
        }
    },
    {
        "name": "Reddit - DevOps",
        "type": "reddit",
        "base_url": "https://oauth.reddit.com",
        "is_active": False,  # Disabled by default (requires credentials)
        "scrape_frequency_hours": 12,
        "config": {
            "client_id": "YOUR_REDDIT_CLIENT_ID",
            "client_secret": "YOUR_REDDIT_CLIENT_SECRET",
            "subreddits": ["devops", "kubernetes", "docker"],
            "max_articles": 20
        }
    },
]


def seed_sources(db: Session) -> int:
    """
    Seed initial sources into the database

    Args:
        db: Database session

    Returns:
        Number of sources created
    """
    created_count = 0

    for source_data in INITIAL_SOURCES:
        # Check if source already exists
        existing = db.query(Source).filter_by(
            type=source_data["type"],
            name=source_data["name"]
        ).first()

        if existing:
            logger.info(f"Source '{source_data['name']}' already exists, skipping")
            continue

        # Create new source
        source = Source(**source_data)
        db.add(source)
        created_count += 1
        logger.info(f"Created source: {source_data['name']}")

    db.commit()
    logger.info(f"Seeding completed: {created_count} sources created")

    return created_count


def main():
    """Main entry point for the seeding script"""
    logger.info("Starting database seeding...")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified")

    # Get database session
    db = next(get_db())

    try:
        # Seed sources
        created = seed_sources(db)

        # Print summary
        total_sources = db.query(Source).count()
        active_sources = db.query(Source).filter_by(is_active=True).count()

        print("\n" + "="*60)
        print("DATABASE SEEDING COMPLETE")
        print("="*60)
        print(f"✓ Sources created: {created}")
        print(f"✓ Total sources in database: {total_sources}")
        print(f"✓ Active sources: {active_sources}")
        print("="*60)

        # List all sources
        print("\nCurrent sources in database:")
        print("-" * 60)
        sources = db.query(Source).all()
        for source in sources:
            status = "✓ ACTIVE" if source.is_active else "✗ INACTIVE"
            print(f"  {status} | {source.name} ({source.type})")
            print(f"           | Frequency: every {source.scrape_frequency_hours}h")
        print("-" * 60)

        # Reddit credentials warning
        reddit_sources = db.query(Source).filter_by(type="reddit").all()
        if reddit_sources:
            print("\n⚠️  IMPORTANT: Reddit Configuration Required")
            print("-" * 60)
            print("Reddit sources require API credentials:")
            print("1. Create Reddit app: https://www.reddit.com/prefs/apps")
            print("2. Update source configs with client_id and client_secret:")
            print("   - Via database directly")
            print("   - Or via API: PUT /api/sources/{id}")
            print("-" * 60)

    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
