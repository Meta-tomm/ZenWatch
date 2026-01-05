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


# Initial keywords configuration for AI agentic ecosystem
INITIAL_KEYWORDS = [
    # Frameworks & Tools
    {"keyword": "langchain", "category": "frameworks", "weight": 2.5},
    {"keyword": "llamaindex", "category": "frameworks", "weight": 2.5},
    {"keyword": "autogpt", "category": "agents", "weight": 2.5},
    {"keyword": "crewai", "category": "agents", "weight": 2.5},
    {"keyword": "semantic kernel", "category": "frameworks", "weight": 2.0},

    # Models & Providers
    {"keyword": "claude", "category": "models", "weight": 3.0},
    {"keyword": "gpt-4", "category": "models", "weight": 3.0},
    {"keyword": "gpt-5", "category": "models", "weight": 3.0},
    {"keyword": "gemini", "category": "models", "weight": 2.5},
    {"keyword": "mistral", "category": "models", "weight": 2.5},
    {"keyword": "llama", "category": "models", "weight": 2.5},

    # Concepts
    {"keyword": "mcp", "category": "concepts", "weight": 3.0},
    {"keyword": "function calling", "category": "concepts", "weight": 2.5},
    {"keyword": "tool use", "category": "concepts", "weight": 2.5},
    {"keyword": "agentic", "category": "concepts", "weight": 3.0},
    {"keyword": "rag", "category": "concepts", "weight": 2.5},
    {"keyword": "fine-tuning", "category": "concepts", "weight": 2.0},
    {"keyword": "prompt engineering", "category": "concepts", "weight": 2.0},

    # Companies
    {"keyword": "openai", "category": "companies", "weight": 3.0},
    {"keyword": "anthropic", "category": "companies", "weight": 3.0},
    {"keyword": "huggingface", "category": "companies", "weight": 2.5},
    {"keyword": "ollama", "category": "tools", "weight": 2.0},

    # General
    {"keyword": "llm", "category": "general", "weight": 2.0},
    {"keyword": "agents", "category": "general", "weight": 2.5},
]


def seed_keywords(db: Session) -> int:
    """
    Seed initial keywords into the database

    Args:
        db: Database session

    Returns:
        Number of keywords created
    """
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
    logger.info("Starting keyword seeding...")

    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified")

    # Get database session
    db = next(get_db())

    try:
        # Seed keywords
        created = seed_keywords(db)

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
