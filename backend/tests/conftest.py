import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base


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

    # Import all models to ensure they're registered
    from app.models import source, scraping_run, article

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    # Cleanup
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()
