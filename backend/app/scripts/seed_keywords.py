"""
Seed initial AI agentic keywords into the database

This script populates the database with pre-configured keywords
for tracking AI/ML and agentic technology trends.

Usage:
    python -m app.scripts.seed_keywords
    # or
    poetry run python -m app.scripts.seed_keywords
"""

from sqlalchemy.orm import Session
from app.database import get_db, engine, Base
from app.models.keyword import Keyword
from app.utils.logger import get_logger

logger = get_logger(__name__)


# Initial keywords configuration for Claude + Data Analytics
INITIAL_KEYWORDS = [
    # Claude AI (focus principal)
    {"keyword": "claude", "category": "claude", "weight": 4.0},
    {"keyword": "anthropic", "category": "claude", "weight": 3.5},
    {"keyword": "claude code", "category": "claude", "weight": 4.0},
    {"keyword": "claude sonnet", "category": "claude", "weight": 3.5},
    {"keyword": "claude opus", "category": "claude", "weight": 3.5},

    # Data Analytics Tools - each with its own category
    {"keyword": "power bi", "category": "power-bi", "weight": 3.0},
    {"keyword": "sql", "category": "sql", "weight": 2.5},
    {"keyword": "excel", "category": "excel", "weight": 2.0},
    {"keyword": "python", "category": "python", "weight": 2.5},
    {"keyword": "pandas", "category": "python", "weight": 2.5},
    {"keyword": "tableau", "category": "tableau", "weight": 3.0},
    {"keyword": "etl", "category": "etl", "weight": 2.5},
    {"keyword": "bigquery", "category": "bigquery", "weight": 2.5},
    {"keyword": "snowflake", "category": "snowflake", "weight": 2.5},
    {"keyword": "dbt", "category": "dbt", "weight": 2.5},
    {"keyword": "jupyter", "category": "python", "weight": 2.0},
    {"keyword": "numpy", "category": "python", "weight": 2.0},
    {"keyword": "matplotlib", "category": "python", "weight": 2.0},

    # Data Roles
    {"keyword": "data analyst", "category": "data-analyst", "weight": 3.5},
    {"keyword": "data science", "category": "data-science", "weight": 3.0},
]


def reset_keywords(db: Session) -> int:
    """
    Delete all existing keywords from the database

    Args:
        db: Database session

    Returns:
        Number of keywords deleted
    """
    deleted_count = db.query(Keyword).delete()
    db.commit()
    logger.info(f"Deleted {deleted_count} existing keywords")
    return deleted_count


def seed_keywords(db: Session, reset: bool = False) -> int:
    """
    Seed initial keywords into the database

    Args:
        db: Database session
        reset: If True, delete all existing keywords first

    Returns:
        Number of keywords created
    """
    if reset:
        reset_keywords(db)

    created_count = 0

    for keyword_data in INITIAL_KEYWORDS:
        # Check if keyword already exists
        existing = db.query(Keyword).filter_by(
            keyword=keyword_data["keyword"]
        ).first()

        if existing:
            logger.info(f"Keyword '{keyword_data['keyword']}' already exists, skipping")
            continue

        # Create new keyword
        keyword = Keyword(**keyword_data)
        db.add(keyword)
        created_count += 1
        logger.info(f"Created keyword: {keyword_data['keyword']}")

    db.commit()
    logger.info(f"Seeding completed: {created_count} keywords created")

    return created_count


def main():
    """Main entry point for the seeding script"""
    import sys

    reset = "--reset" in sys.argv
    if reset:
        logger.info("Starting keyword seeding with RESET (deleting existing keywords)...")
    else:
        logger.info("Starting keyword seeding...")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified")

    # Get database session
    db = next(get_db())

    try:
        # Seed keywords
        created = seed_keywords(db, reset=reset)

        # Print summary
        total_keywords = db.query(Keyword).count()
        active_keywords = db.query(Keyword).filter_by(is_active=True).count()

        print("\n" + "="*60)
        print("KEYWORD SEEDING COMPLETE")
        print("="*60)
        print(f"Keywords created: {created}")
        print(f"Total keywords in database: {total_keywords}")
        print(f"Active keywords: {active_keywords}")
        print("="*60)

        # List keywords by category
        print("\nKeywords by category:")
        print("-" * 60)

        categories = db.query(Keyword.category).distinct().all()
        for (category,) in sorted(categories, key=lambda x: x[0] or ""):
            keywords_in_cat = db.query(Keyword).filter_by(category=category).all()
            print(f"\n  [{category.upper() if category else 'UNCATEGORIZED'}]")
            for kw in keywords_in_cat:
                status = "ACTIVE" if kw.is_active else "INACTIVE"
                print(f"    - {kw.keyword} (weight: {kw.weight}, {status})")

        print("-" * 60)

    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
