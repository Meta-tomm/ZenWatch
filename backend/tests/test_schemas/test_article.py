import pytest
from datetime import datetime
from pydantic import ValidationError
from app.schemas.article import ArticleCreate


def test_article_create_valid():
    data = {
        "title": "Test Article",
        "url": "https://example.com",
        "published_at": datetime.now()
    }
    article = ArticleCreate(**data)
    assert article.title == "Test Article"


def test_article_create_invalid_url():
    data = {"title": "Test", "url": "not-a-url", "published_at": datetime.now()}
    with pytest.raises(ValidationError):
        ArticleCreate(**data)


def test_article_create_missing_title():
    data = {"url": "https://example.com", "published_at": datetime.now()}
    with pytest.raises(ValidationError):
        ArticleCreate(**data)
