import pytest
from app.scripts.seed_sources import seed_sources, INITIAL_SOURCES
from app.models.source import Source


def test_seed_sources_creates_all_sources(db_session):
    """Test that seed_sources creates all initial sources"""

    # Run seeding
    created_count = seed_sources(db_session)

    # Verify correct number of sources created
    assert created_count == len(INITIAL_SOURCES)

    # Verify sources exist in database
    total_sources = db_session.query(Source).count()
    assert total_sources == len(INITIAL_SOURCES)


def test_seed_sources_does_not_duplicate(db_session):
    """Test that running seed twice doesn't create duplicates"""

    # First seeding
    first_count = seed_sources(db_session)
    assert first_count == len(INITIAL_SOURCES)

    # Second seeding (should skip existing)
    second_count = seed_sources(db_session)
    assert second_count == 0

    # Verify total is still the same
    total_sources = db_session.query(Source).count()
    assert total_sources == len(INITIAL_SOURCES)


def test_seed_sources_creates_hackernews_source(db_session):
    """Test that HackerNews source is created correctly"""

    seed_sources(db_session)

    hn_source = db_session.query(Source).filter_by(type="hackernews").first()

    assert hn_source is not None
    assert hn_source.name == "HackerNews"
    assert hn_source.is_active == True
    assert hn_source.scrape_frequency_hours == 6
    assert "max_articles" in hn_source.config


def test_seed_sources_creates_reddit_sources(db_session):
    """Test that Reddit sources are created correctly"""

    seed_sources(db_session)

    reddit_sources = db_session.query(Source).filter_by(type="reddit").all()

    assert len(reddit_sources) == 3  # Programming, AI/ML, DevOps

    # Check Programming source
    prog_source = db_session.query(Source).filter_by(
        name="Reddit - Programming"
    ).first()
    assert prog_source is not None
    assert prog_source.is_active == True
    assert "subreddits" in prog_source.config
    assert "programming" in prog_source.config["subreddits"]


def test_seed_sources_has_active_and_inactive(db_session):
    """Test that there are both active and inactive sources"""

    seed_sources(db_session)

    active_count = db_session.query(Source).filter_by(is_active=True).count()
    inactive_count = db_session.query(Source).filter_by(is_active=False).count()

    assert active_count > 0
    assert inactive_count > 0  # DevOps source is inactive by default


def test_initial_sources_data_structure():
    """Test that INITIAL_SOURCES has correct structure"""

    required_fields = ["name", "type", "base_url", "is_active",
                      "scrape_frequency_hours", "config"]

    for source in INITIAL_SOURCES:
        for field in required_fields:
            assert field in source, f"Missing field '{field}' in source"

        # Verify config has required fields
        assert isinstance(source["config"], dict)

        # Reddit sources need credentials fields
        if source["type"] == "reddit":
            assert "client_id" in source["config"]
            assert "client_secret" in source["config"]
            assert "subreddits" in source["config"]
