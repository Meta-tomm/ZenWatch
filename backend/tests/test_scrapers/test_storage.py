import pytest
from datetime import datetime
from app.scrapers.storage import save_articles
from app.models.article import Article


@pytest.mark.asyncio
async def test_save_new_article(db_session):
    """Test saving a new article"""
    articles = [{
        'title': 'Test Article',
        'url': 'https://example.com/test',
        'source_type': 'reddit',
        'published_at': datetime.now()
    }]

    saved = await save_articles(articles, 'reddit', db_session)
    assert saved == 1

    # Verify article was saved
    article = db_session.query(Article).filter_by(url='https://example.com/test').first()
    assert article is not None
    assert article.title == 'Test Article'
    assert article.source_type == 'reddit'


@pytest.mark.asyncio
async def test_save_duplicate_article(db_session):
    """Test that duplicate URLs are updated, not duplicated"""
    articles = [{
        'title': 'Original Title',
        'url': 'https://example.com/duplicate',
        'source_type': 'reddit',
        'published_at': datetime.now(),
        'upvotes': 10
    }]

    # First save
    saved = await save_articles(articles, 'reddit', db_session)
    assert saved == 1

    # Update same URL with new data
    updated_articles = [{
        'title': 'Updated Title',
        'url': 'https://example.com/duplicate',
        'source_type': 'reddit',
        'published_at': datetime.now(),
        'upvotes': 50
    }]

    saved = await save_articles(updated_articles, 'reddit', db_session)
    assert saved == 1

    # Verify only one article exists
    articles_count = db_session.query(Article).filter_by(url='https://example.com/duplicate').count()
    assert articles_count == 1

    # Verify article was updated
    article = db_session.query(Article).filter_by(url='https://example.com/duplicate').first()
    assert article.title == 'Updated Title'
    assert article.upvotes == 50


@pytest.mark.asyncio
async def test_save_multiple_articles(db_session):
    """Test saving multiple articles at once"""
    articles = [
        {
            'title': f'Article {i}',
            'url': f'https://example.com/article{i}',
            'source_type': 'hackernews',
            'published_at': datetime.now()
        }
        for i in range(5)
    ]

    saved = await save_articles(articles, 'hackernews', db_session)
    assert saved == 5

    # Verify all articles were saved
    count = db_session.query(Article).filter_by(source_type='hackernews').count()
    assert count == 5


@pytest.mark.asyncio
async def test_save_articles_with_optional_fields(db_session):
    """Test saving articles with all optional fields"""
    articles = [{
        'title': 'Full Article',
        'url': 'https://example.com/full',
        'source_type': 'reddit',
        'published_at': datetime.now(),
        'content': 'Article content here',
        'author': 'john_doe',
        'upvotes': 100,
        'comments_count': 25,
        'tags': ['python', 'fastapi'],
        'external_id': 'reddit_123'
    }]

    saved = await save_articles(articles, 'reddit', db_session)
    assert saved == 1

    article = db_session.query(Article).filter_by(url='https://example.com/full').first()
    assert article.content == 'Article content here'
    assert article.author == 'john_doe'
    assert article.upvotes == 100
    assert article.comments_count == 25
    assert article.tags == ['python', 'fastapi']
    assert article.external_id == 'reddit_123'
