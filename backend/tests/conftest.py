import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base
import fakeredis.aioredis


@pytest.fixture(scope="function")
def db_session():
    """
    Create an in-memory SQLite database for testing

    Scope: function - creates a fresh database for each test
    """
    # Create in-memory SQLite database with thread checking disabled
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool  # Use static pool for thread safety
    )

    # Import models needed for tests
    # Note: user_config excluded due to SQLite incompatibility with ARRAY types
    from app.models import source, scraping_run, article, youtube_channel

    # Create only the tables we need (exclude user_config)
    tables_to_create = [
        Base.metadata.tables['sources'],
        Base.metadata.tables['scraping_runs'],
        Base.metadata.tables['articles'],
        Base.metadata.tables['article_keywords'],
        Base.metadata.tables['youtube_channels'],
    ]

    for table in tables_to_create:
        table.create(engine, checkfirst=True)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
async def redis_client():
    """
    Create fake Redis client for testing

    Uses fakeredis to avoid needing actual Redis instance
    Scope: function - creates fresh Redis for each test
    """
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)

    yield client

    # Cleanup
    await client.flushall()
    await client.aclose()
