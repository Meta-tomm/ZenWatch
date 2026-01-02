"""
Integration tests for complete scraping workflow

Tests the full end-to-end flow:
1. Trigger scraping via Celery task
2. Scrape from multiple sources (Reddit, HackerNews)
3. Save articles to database
4. Verify data integrity
"""

import pytest
import respx
import httpx
from unittest.mock import patch, Mock
from sqlalchemy.orm import Session

from app.models.source import Source
from app.models.article import Article
from app.models.scraping_run import ScrapingRun
from app.tasks.scraping import scrape_all_sources_async
from app.scrapers.registry import ScraperRegistry

# Import plugins to trigger auto-registration
from app.scrapers.plugins import reddit, hackernews


@pytest.fixture
def setup_sources(db_session: Session):
    """Create test sources in database"""
    sources = [
        Source(
            name="Test HackerNews",
            type="hackernews",
            base_url="https://hacker-news.firebaseio.com/v0",
            is_active=True,
            config={"max_articles": 5, "story_type": "top"}
        ),
        Source(
            name="Test Reddit",
            type="reddit",
            base_url="https://oauth.reddit.com",
            is_active=True,
            config={
                "client_id": "test_client_id",
                "client_secret": "test_client_secret",
                "subreddits": ["python"],
                "max_articles": 3
            }
        ),
        Source(
            name="Inactive Source",
            type="hackernews",
            base_url="https://hacker-news.firebaseio.com/v0",
            is_active=False,
            config={"max_articles": 10}
        )
    ]

    for source in sources:
        db_session.add(source)
    db_session.commit()

    return sources


@pytest.mark.asyncio
@respx.mock
async def test_end_to_end_scraping_flow(db_session: Session, setup_sources):
    """Test complete scraping workflow with mocked HTTP responses"""

    # Mock HackerNews API responses
    respx.get("https://hacker-news.firebaseio.com/v0/topstories.json").mock(
        return_value=httpx.Response(200, json=[1, 2, 3, 4, 5])
    )

    # Mock HackerNews story details
    for story_id in [1, 2, 3, 4, 5]:
        respx.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json").mock(
            return_value=httpx.Response(200, json={
                "id": story_id,
                "title": f"HN Story {story_id} about python",
                "url": f"https://example.com/hn-{story_id}",
                "by": "testuser",
                "time": 1609459200,
                "score": 100 + story_id,
                "descendants": 10
            })
        )

    # Mock Reddit OAuth token
    respx.post("https://www.reddit.com/api/v1/access_token").mock(
        return_value=httpx.Response(200, json={
            "access_token": "test_token_123",
            "token_type": "bearer",
            "expires_in": 3600
        })
    )

    # Mock Reddit subreddit posts
    respx.get("https://oauth.reddit.com/r/python/hot").mock(
        return_value=httpx.Response(200, json={
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "abc123",
                            "title": "Great Python tutorial",
                            "url": "https://example.com/python-tuto",
                            "selftext": "This is a great tutorial about Python",
                            "author": "pythonista",
                            "created_utc": 1609459200,
                            "ups": 250,
                            "num_comments": 45,
                            "subreddit": "python"
                        }
                    },
                    {
                        "data": {
                            "id": "def456",
                            "title": "Python 3.12 released",
                            "url": "https://example.com/python-3.12",
                            "selftext": "",
                            "author": "pydev",
                            "created_utc": 1609459300,
                            "ups": 500,
                            "num_comments": 120,
                            "subreddit": "python"
                        }
                    }
                ]
            }
        })
    )

    # Execute scraping
    keywords = ["python", "tutorial"]
    task_id = "test_task_123"

    result = await scrape_all_sources_async(db_session, keywords, task_id)

    # Verify result
    assert result["status"] == "success"
    assert result["total_articles"] > 0
    assert "sources_scraped" in result

    # Verify articles in database
    articles = db_session.query(Article).all()
    assert len(articles) > 0

    # Verify HackerNews articles
    hn_articles = db_session.query(Article).filter_by(source_type="hackernews").all()
    assert len(hn_articles) == 5
    for article in hn_articles:
        assert "python" in article.title.lower()
        assert article.url.startswith("https://example.com/hn-")
        assert article.upvotes > 100

    # Verify Reddit articles
    reddit_articles = db_session.query(Article).filter_by(source_type="reddit").all()
    assert len(reddit_articles) == 2
    for article in reddit_articles:
        assert article.url in [
            "https://example.com/python-tuto",
            "https://example.com/python-3.12"
        ]

    # Verify scraping run was recorded
    scraping_run = db_session.query(ScrapingRun).filter_by(task_id=task_id).first()
    assert scraping_run is not None
    assert scraping_run.status == "success"
    assert scraping_run.articles_scraped == result["total_articles"]
    assert scraping_run.articles_saved == result["total_articles"]
    assert scraping_run.completed_at is not None


@pytest.mark.asyncio
@respx.mock
async def test_scraping_with_no_active_sources(db_session: Session):
    """Test scraping when all sources are inactive"""

    # Create only inactive source
    source = Source(
        name="Inactive HackerNews",
        type="hackernews",
        base_url="https://hacker-news.firebaseio.com/v0",
        is_active=False,
        config={"max_articles": 10}
    )
    db_session.add(source)
    db_session.commit()

    # Execute scraping
    result = await scrape_all_sources_async(db_session, ["python"], "task_456")

    # Should complete but with 0 articles
    assert result["status"] in ["success", "failed"]  # No sources means could be either
    assert result["total_articles"] == 0
    assert result["sources_scraped"] == 0


@pytest.mark.asyncio
@respx.mock
async def test_scraping_handles_http_errors_gracefully(db_session: Session):
    """Test that scraping continues even when one source fails"""

    # Create sources
    hn_source = Source(
        name="Failing HackerNews",
        type="hackernews",
        base_url="https://hacker-news.firebaseio.com/v0",
        is_active=True,
        config={"max_articles": 5}
    )
    reddit_source = Source(
        name="Working Reddit",
        type="reddit",
        base_url="https://oauth.reddit.com",
        is_active=True,
        config={
            "client_id": "test_id",
            "client_secret": "test_secret",
            "subreddits": ["python"],
            "max_articles": 3
        }
    )
    db_session.add_all([hn_source, reddit_source])
    db_session.commit()

    # Mock HackerNews to fail
    respx.get("https://hacker-news.firebaseio.com/v0/topstories.json").mock(
        return_value=httpx.Response(500, json={"error": "Internal Server Error"})
    )

    # Mock Reddit to succeed
    respx.post("https://www.reddit.com/api/v1/access_token").mock(
        return_value=httpx.Response(200, json={
            "access_token": "test_token",
            "token_type": "bearer",
            "expires_in": 3600
        })
    )

    respx.get("https://oauth.reddit.com/r/python/hot").mock(
        return_value=httpx.Response(200, json={
            "data": {
                "children": [
                    {
                        "data": {
                            "id": "xyz789",
                            "title": "Python rocks",
                            "url": "https://example.com/python-rocks",
                            "selftext": "Content here",
                            "author": "user",
                            "created_utc": 1609459200,
                            "ups": 100,
                            "num_comments": 10,
                            "subreddit": "python"
                        }
                    }
                ]
            }
        })
    )

    # Execute scraping
    result = await scrape_all_sources_async(db_session, ["python"], "task_789")

    # Should have partial success (one source failed, one succeeded)
    assert result["status"] in ["success", "partial_success"]
    assert result["total_articles"] >= 1

    # Verify only Reddit articles were saved
    articles = db_session.query(Article).all()
    assert all(article.source_type == "reddit" for article in articles)


@pytest.mark.asyncio
@respx.mock
async def test_scraping_deduplicates_articles(db_session: Session, setup_sources):
    """Test that duplicate articles are not created"""

    # Mock HackerNews API
    respx.get("https://hacker-news.firebaseio.com/v0/topstories.json").mock(
        return_value=httpx.Response(200, json=[1])
    )

    respx.get("https://hacker-news.firebaseio.com/v0/item/1.json").mock(
        return_value=httpx.Response(200, json={
            "id": 1,
            "title": "Duplicate Python Article",
            "url": "https://example.com/duplicate",
            "by": "testuser",
            "time": 1609459200,
            "score": 100,
            "descendants": 10
        })
    )

    # Mock Reddit OAuth
    respx.post("https://www.reddit.com/api/v1/access_token").mock(
        return_value=httpx.Response(200, json={
            "access_token": "test_token",
            "token_type": "bearer",
            "expires_in": 3600
        })
    )

    respx.get("https://oauth.reddit.com/r/python/hot").mock(
        return_value=httpx.Response(200, json={"data": {"children": []}})
    )

    # First scraping run
    await scrape_all_sources_async(db_session, ["python"], "task_1")

    first_count = db_session.query(Article).count()
    assert first_count > 0

    # Second scraping run (same data)
    await scrape_all_sources_async(db_session, ["python"], "task_2")

    second_count = db_session.query(Article).count()

    # Count should be the same (no duplicates)
    assert second_count == first_count

    # Verify the article was updated, not duplicated
    article = db_session.query(Article).filter_by(
        url="https://example.com/duplicate"
    ).all()
    assert len(article) == 1


@pytest.mark.asyncio
async def test_scraping_with_invalid_source_type(db_session: Session):
    """Test handling of invalid source type"""

    # Create source with non-existent scraper type
    source = Source(
        name="Invalid Source",
        type="nonexistent_scraper",
        base_url="https://example.com",
        is_active=True,
        config={"test": "config"}
    )
    db_session.add(source)
    db_session.commit()

    # Execute scraping
    result = await scrape_all_sources_async(db_session, ["python"], "task_invalid")

    # Should complete but skip invalid source
    assert result["status"] in ["success", "failed"]
    assert result["total_articles"] == 0


@pytest.mark.asyncio
@respx.mock
async def test_scraping_with_empty_keywords(db_session: Session, setup_sources):
    """Test scraping with no keyword filtering"""

    # Mock minimal responses
    respx.get("https://hacker-news.firebaseio.com/v0/topstories.json").mock(
        return_value=httpx.Response(200, json=[1])
    )

    respx.get("https://hacker-news.firebaseio.com/v0/item/1.json").mock(
        return_value=httpx.Response(200, json={
            "id": 1,
            "title": "Some random article",
            "url": "https://example.com/random",
            "by": "user",
            "time": 1609459200,
            "score": 50,
            "descendants": 5
        })
    )

    respx.post("https://www.reddit.com/api/v1/access_token").mock(
        return_value=httpx.Response(200, json={
            "access_token": "token",
            "token_type": "bearer",
            "expires_in": 3600
        })
    )

    respx.get("https://oauth.reddit.com/r/python/hot").mock(
        return_value=httpx.Response(200, json={"data": {"children": []}})
    )

    # Scrape with empty keywords (should get all articles)
    result = await scrape_all_sources_async(db_session, [], "task_no_keywords")

    assert result["status"] == "success"
    # Should still get articles even without keyword filtering
    assert result["total_articles"] >= 1


@pytest.mark.asyncio
@respx.mock
async def test_scraping_respects_max_articles_limit(db_session: Session):
    """Test that scrapers respect the max_articles config"""

    # Create source with max_articles = 2
    source = Source(
        name="Limited HackerNews",
        type="hackernews",
        base_url="https://hacker-news.firebaseio.com/v0",
        is_active=True,
        config={"max_articles": 2, "story_type": "top"}
    )
    db_session.add(source)
    db_session.commit()

    # Mock API to return 10 stories
    respx.get("https://hacker-news.firebaseio.com/v0/topstories.json").mock(
        return_value=httpx.Response(200, json=list(range(1, 11)))
    )

    # Mock story details for first 3 (scraper should only fetch 2)
    for story_id in range(1, 4):
        respx.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json").mock(
            return_value=httpx.Response(200, json={
                "id": story_id,
                "title": f"Story {story_id}",
                "url": f"https://example.com/{story_id}",
                "by": "user",
                "time": 1609459200,
                "score": 100,
                "descendants": 10
            })
        )

    # Execute scraping
    result = await scrape_all_sources_async(db_session, [], "task_limit")

    # Should only get 2 articles
    articles = db_session.query(Article).all()
    assert len(articles) == 2
