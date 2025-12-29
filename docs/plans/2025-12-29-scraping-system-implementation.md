# Scraping System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Implémenter un système de scraping multi-sources scalable avec architecture plugin pour TechWatch.

**Architecture:** Plugin architecture avec auto-découverte, strategies réutilisables (RateLimiter, RetryStrategy), orchestration Celery semi-parallèle, triggers scheduled (Celery Beat) et on-demand (API).

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy, Celery, Redis, httpx, BeautifulSoup, Pydantic, pytest

---

## Task 1: Database Migrations

**Files:**
- Create: `backend/alembic/versions/001_add_sources_table.py`
- Create: `backend/alembic/versions/002_add_scraping_runs_table.py`

**Step 1: Create sources table migration**

```bash
cd backend
poetry run alembic revision -m "add sources table"
```

**Step 2: Write migration for sources table**

Edit the generated migration file:

```python
def upgrade():
    op.create_table(
        'sources',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(50), nullable=False, unique=True),
        sa.Column('base_url', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('scrape_frequency_hours', sa.Integer(), default=6),
        sa.Column('last_scraped_at', sa.DateTime(), nullable=True),
        sa.Column('config', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )

def downgrade():
    op.drop_table('sources')
```

**Step 3: Run migration**

```bash
poetry run alembic upgrade head
```

Expected: Migration applies successfully, table `sources` created

**Step 4: Create scraping_runs table migration**

```bash
poetry run alembic revision -m "add scraping_runs table"
```

**Step 5: Write migration for scraping_runs**

```python
def upgrade():
    op.create_table(
        'scraping_runs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_id', sa.String(255), unique=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('articles_scraped', sa.Integer(), default=0),
        sa.Column('articles_saved', sa.Integer(), default=0),
        sa.Column('error_message', sa.Text(), nullable=True)
    )
    op.create_index('idx_scraping_runs_task_id', 'scraping_runs', ['task_id'])

def downgrade():
    op.drop_index('idx_scraping_runs_task_id')
    op.drop_table('scraping_runs')
```

**Step 6: Run migration**

```bash
poetry run alembic upgrade head
```

**Step 7: Commit migrations**

```bash
git add backend/alembic/versions/
git commit -m "feat(db): add sources and scraping_runs tables"
```

---

## Task 2: SQLAlchemy Models

**Files:**
- Modify: `backend/app/models/source.py`
- Create: `backend/app/models/scraping_run.py`

**Step 1: Write test for Source model**

Create: `backend/tests/test_models/test_source.py`

```python
import pytest
from app.models.source import Source
from app.database import get_db

def test_source_model_creation():
    source = Source(
        name="Reddit",
        type="reddit",
        config={"subreddits": ["programming"]},
        is_active=True
    )
    assert source.name == "Reddit"
    assert source.type == "reddit"
    assert source.is_active == True
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_models/test_source.py -v
```

Expected: FAIL - Source model not defined

**Step 3: Implement Source model**

Create: `backend/app/models/source.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from app.database import Base

class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(50), nullable=False, unique=True)
    base_url = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    scrape_frequency_hours = Column(Integer, default=6)
    last_scraped_at = Column(DateTime, nullable=True)
    config = Column(JSON, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

**Step 4: Run test to verify it passes**

```bash
poetry run pytest tests/test_models/test_source.py -v
```

Expected: PASS

**Step 5: Write test for ScrapingRun model**

Create: `backend/tests/test_models/test_scraping_run.py`

```python
from app.models.scraping_run import ScrapingRun

def test_scraping_run_model():
    run = ScrapingRun(
        task_id="test-123",
        source_type="reddit",
        status="success",
        articles_scraped=50
    )
    assert run.task_id == "test-123"
    assert run.status == "success"
```

**Step 6: Run test to verify it fails**

```bash
poetry run pytest tests/test_models/test_scraping_run.py -v
```

**Step 7: Implement ScrapingRun model**

Create: `backend/app/models/scraping_run.py`

```python
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base

class ScrapingRun(Base):
    __tablename__ = "scraping_runs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(255), unique=True, index=True)
    source_type = Column(String(50), nullable=False)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), nullable=False)
    articles_scraped = Column(Integer, default=0)
    articles_saved = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
```

**Step 8: Run test**

```bash
poetry run pytest tests/test_models/test_scraping_run.py -v
```

**Step 9: Commit models**

```bash
git add backend/app/models/ backend/tests/test_models/
git commit -m "feat(models): add Source and ScrapingRun models"
```

---

## Task 3: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/article.py`
- Create: `backend/tests/test_schemas/test_article.py`

**Step 1: Write test for ArticleCreate schema**

```python
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
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_schemas/test_article.py -v
```

**Step 3: Implement ArticleCreate schema**

Create: `backend/app/schemas/article.py`

```python
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class ArticleCreate(BaseModel):
    # Champs obligatoires
    title: str = Field(..., min_length=1, max_length=500)
    url: str = Field(..., pattern=r'^https?://')
    published_at: datetime

    # Champs optionnels
    content: Optional[str] = Field(None, max_length=50000)
    author: Optional[str] = None
    upvotes: Optional[int] = 0
    comments_count: Optional[int] = 0
    tags: Optional[List[str]] = []
    language: Optional[str] = 'en'
    read_time_minutes: Optional[int] = None

    @field_validator('url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        if not v.startswith(('http://', 'https://')):
            raise ValueError('URL must start with http:// or https://')
        return v

class ArticleResponse(ArticleCreate):
    id: int
    source_type: str
    score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True
```

**Step 4: Run tests**

```bash
poetry run pytest tests/test_schemas/test_article.py -v
```

**Step 5: Commit schemas**

```bash
git add backend/app/schemas/ backend/tests/test_schemas/
git commit -m "feat(schemas): add ArticleCreate and ArticleResponse schemas"
```

---

## Task 4: Base ScraperPlugin Interface

**Files:**
- Create: `backend/app/scrapers/base.py`
- Create: `backend/tests/test_scrapers/test_base.py`

**Step 1: Write test for ScraperPlugin interface**

```python
import pytest
from app.scrapers.base import ScraperPlugin

def test_scraper_plugin_is_abstract():
    with pytest.raises(TypeError):
        ScraperPlugin()

def test_scraper_plugin_requires_scrape_method():
    class InvalidScraper(ScraperPlugin):
        pass

    with pytest.raises(TypeError):
        InvalidScraper()
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_scrapers/test_base.py -v
```

**Step 3: Implement ScraperPlugin base class**

Create: `backend/app/scrapers/base.py`

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import httpx

class ScraperPlugin(ABC):
    """Interface de base pour tous les scrapers"""

    name: str
    display_name: str
    version: str

    def __init__(self):
        self.client: Optional[httpx.AsyncClient] = None

    @abstractmethod
    async def scrape(self, config: Dict, keywords: List[str]) -> List[Dict]:
        """
        Scrape articles depuis la source.

        Args:
            config: Configuration spécifique au scraper (depuis DB)
            keywords: Liste des mots-clés pour filtrage

        Returns:
            Liste de dictionnaires représentant les articles
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict) -> bool:
        """
        Valide la configuration du scraper.

        Args:
            config: Configuration à valider

        Returns:
            True si valide, False sinon
        """
        pass

    async def _quick_match(self, title: str, keywords: List[str]) -> bool:
        """
        Quick keyword match sur le titre.

        Args:
            title: Titre de l'article
            keywords: Liste des mots-clés

        Returns:
            True si au moins un keyword est présent
        """
        title_lower = title.lower()
        return any(kw.lower() in title_lower for kw in keywords)

    async def __aenter__(self):
        """Context manager pour httpx.AsyncClient"""
        self.client = httpx.AsyncClient(timeout=30.0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Ferme le client HTTP"""
        if self.client:
            await self.client.aclose()
```

**Step 4: Run tests**

```bash
poetry run pytest tests/test_scrapers/test_base.py -v
```

**Step 5: Test quick_match functionality**

Add to test file:

```python
import pytest
from app.scrapers.base import ScraperPlugin

class ConcreteScraper(ScraperPlugin):
    name = "test"
    display_name = "Test"
    version = "1.0.0"

    async def scrape(self, config, keywords):
        return []

    def validate_config(self, config):
        return True

@pytest.mark.asyncio
async def test_quick_match():
    scraper = ConcreteScraper()
    keywords = ["python", "django"]

    assert await scraper._quick_match("Learn Python Programming", keywords) == True
    assert await scraper._quick_match("Django REST Framework", keywords) == True
    assert await scraper._quick_match("Java Spring Boot", keywords) == False
```

**Step 6: Run tests**

```bash
poetry run pytest tests/test_scrapers/test_base.py -v
```

**Step 7: Commit**

```bash
git add backend/app/scrapers/base.py backend/tests/test_scrapers/test_base.py
git commit -m "feat(scrapers): add ScraperPlugin base interface"
```

---

## Task 5: Plugin Registry

**Files:**
- Create: `backend/app/scrapers/registry.py`
- Create: `backend/tests/test_scrapers/test_registry.py`

**Step 1: Write test for plugin registration**

```python
import pytest
from app.scrapers.registry import ScraperRegistry, scraper_plugin
from app.scrapers.base import ScraperPlugin

def test_registry_singleton():
    r1 = ScraperRegistry()
    r2 = ScraperRegistry()
    assert r1 is r2

def test_scraper_plugin_decorator():
    @scraper_plugin(name="test", display_name="Test", version="1.0")
    class TestScraper(ScraperPlugin):
        async def scrape(self, config, keywords):
            return []
        def validate_config(self, config):
            return True

    assert TestScraper.name == "test"
    assert TestScraper.display_name == "Test"

def test_registry_get_scraper():
    registry = ScraperRegistry()
    registry.clear()  # Reset pour test

    @scraper_plugin(name="mock", display_name="Mock", version="1.0")
    class MockScraper(ScraperPlugin):
        async def scrape(self, config, keywords):
            return []
        def validate_config(self, config):
            return True

    scraper = registry.get("mock")
    assert scraper is not None
    assert isinstance(scraper, MockScraper)
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_scrapers/test_registry.py -v
```

**Step 3: Implement ScraperRegistry**

Create: `backend/app/scrapers/registry.py`

```python
from typing import Dict, Type, Optional
from app.scrapers.base import ScraperPlugin
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ScraperRegistry:
    """Singleton registry pour tous les scrapers plugins"""

    _instance = None
    _plugins: Dict[str, Type[ScraperPlugin]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def register(self, name: str, plugin_class: Type[ScraperPlugin]):
        """Enregistre un plugin scraper"""
        self._plugins[name] = plugin_class
        logger.info(f"Registered scraper plugin: {name}")

    def get(self, name: str) -> Optional[ScraperPlugin]:
        """Récupère une instance du plugin"""
        plugin_class = self._plugins.get(name)
        if plugin_class:
            return plugin_class()
        logger.warning(f"Scraper plugin not found: {name}")
        return None

    def list_plugins(self) -> Dict[str, Type[ScraperPlugin]]:
        """Liste tous les plugins enregistrés"""
        return self._plugins.copy()

    def clear(self):
        """Clear registry (pour tests)"""
        self._plugins.clear()

def scraper_plugin(name: str, display_name: str, version: str, required_config: list = None):
    """
    Décorateur pour auto-registration des scrapers.

    Usage:
        @scraper_plugin(name="reddit", display_name="Reddit", version="1.0.0")
        class RedditScraper(ScraperPlugin):
            ...
    """
    def decorator(cls: Type[ScraperPlugin]):
        # Ajouter métadonnées
        cls.name = name
        cls.display_name = display_name
        cls.version = version
        cls.required_config = required_config or []

        # Auto-register
        registry = ScraperRegistry()
        registry.register(name, cls)

        return cls

    return decorator
```

**Step 4: Run tests**

```bash
poetry run pytest tests/test_scrapers/test_registry.py -v
```

**Step 5: Commit**

```bash
git add backend/app/scrapers/registry.py backend/tests/test_scrapers/test_registry.py
git commit -m "feat(scrapers): add plugin registry with auto-discovery"
```

---

## Task 6: RateLimiter Strategy

**Files:**
- Create: `backend/app/scrapers/strategies/rate_limit.py`
- Create: `backend/tests/test_scrapers/test_rate_limiter.py`

**Step 1: Write test for RateLimiter**

```python
import pytest
import asyncio
import time
from app.scrapers.strategies.rate_limit import RateLimiter

@pytest.mark.asyncio
async def test_rate_limiter_allows_requests():
    limiter = RateLimiter(requests_per_minute=120)  # 2 req/sec

    start = time.time()
    async with limiter:
        pass
    async with limiter:
        pass
    elapsed = time.time() - start

    assert elapsed < 1.0  # Should be fast for 2 requests

@pytest.mark.asyncio
async def test_rate_limiter_throttles():
    limiter = RateLimiter(requests_per_minute=60)  # 1 req/sec

    tasks = []
    for _ in range(3):
        async def task():
            async with limiter:
                return time.time()
        tasks.append(task())

    start = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start

    # 3 requests at 1 req/sec should take ~2 seconds
    assert elapsed >= 2.0
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_scrapers/test_rate_limiter.py -v
```

**Step 3: Implement RateLimiter**

Create: `backend/app/scrapers/strategies/rate_limit.py`

```python
import asyncio
import time
from typing import Optional

class RateLimiter:
    """
    Token bucket rate limiter.

    Args:
        requests_per_minute: Nombre de requêtes autorisées par minute
    """

    def __init__(self, requests_per_minute: int = 60):
        self.rate = requests_per_minute
        self.tokens = float(requests_per_minute)
        self.last_update = time.time()
        self.lock = asyncio.Lock()

    async def __aenter__(self):
        async with self.lock:
            await self._wait_for_token()
            self.tokens -= 1
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def _wait_for_token(self):
        """Attend qu'un token soit disponible"""
        while self.tokens < 1:
            await asyncio.sleep(0.1)
            self._refill_tokens()

    def _refill_tokens(self):
        """Remplit les tokens basé sur le temps écoulé"""
        now = time.time()
        elapsed = now - self.last_update
        # Ajouter tokens basé sur le taux (rate/60 tokens par seconde)
        self.tokens = min(self.rate, self.tokens + (elapsed * self.rate / 60))
        self.last_update = now
```

**Step 4: Run tests**

```bash
poetry run pytest tests/test_scrapers/test_rate_limiter.py -v
```

**Step 5: Commit**

```bash
git add backend/app/scrapers/strategies/rate_limit.py backend/tests/test_scrapers/test_rate_limiter.py
git commit -m "feat(strategies): add RateLimiter with token bucket algorithm"
```

---

## Task 7: RetryStrategy

**Files:**
- Create: `backend/app/scrapers/strategies/retry.py`
- Create: `backend/tests/test_scrapers/test_retry.py`

**Step 1: Write test for RetryStrategy**

```python
import pytest
import httpx
from app.scrapers.strategies.retry import RetryStrategy, MaxRetriesExceeded

@pytest.mark.asyncio
async def test_retry_succeeds_on_first_attempt():
    strategy = RetryStrategy(max_retries=3)

    async def succeeding_task():
        return "success"

    result = await strategy.execute(succeeding_task())
    assert result == "success"

@pytest.mark.asyncio
async def test_retry_succeeds_after_failures():
    strategy = RetryStrategy(max_retries=3, backoff_factor=0.1)
    attempts = []

    async def failing_then_succeeding():
        attempts.append(1)
        if len(attempts) < 3:
            raise httpx.HTTPError("Temporary error")
        return "success"

    result = await strategy.execute(failing_then_succeeding())
    assert result == "success"
    assert len(attempts) == 3

@pytest.mark.asyncio
async def test_retry_exhausts_retries():
    strategy = RetryStrategy(max_retries=2, backoff_factor=0.1)

    async def always_failing():
        raise httpx.HTTPError("Permanent error")

    with pytest.raises(MaxRetriesExceeded):
        await strategy.execute(always_failing())
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_scrapers/test_retry.py -v
```

**Step 3: Implement RetryStrategy**

Create: `backend/app/scrapers/strategies/retry.py`

```python
import asyncio
import random
from typing import Coroutine, TypeVar
import httpx
from app.utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')

class MaxRetriesExceeded(Exception):
    """Exception levée quand max retries atteint"""
    pass

class RetryStrategy:
    """
    Retry avec backoff exponentiel + jitter.

    Args:
        max_retries: Nombre max de tentatives
        backoff_factor: Facteur de backoff exponentiel
    """

    def __init__(self, max_retries: int = 3, backoff_factor: float = 2):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    async def execute(self, coro: Coroutine[None, None, T]) -> T:
        """
        Exécute la coroutine avec retry logic.

        Args:
            coro: Coroutine à exécuter

        Returns:
            Résultat de la coroutine

        Raises:
            MaxRetriesExceeded: Si max retries atteint
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                return await coro
            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                last_exception = e

                if attempt < self.max_retries - 1:
                    # Backoff exponentiel avec jitter
                    wait_time = (self.backoff_factor ** attempt) + random.uniform(0, 1)
                    logger.warning(
                        f"Retry {attempt + 1}/{self.max_retries} after {wait_time:.2f}s. Error: {e}"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Max retries ({self.max_retries}) exceeded. Last error: {e}")

        raise MaxRetriesExceeded(
            f"Failed after {self.max_retries} retries"
        ) from last_exception
```

**Step 4: Run tests**

```bash
poetry run pytest tests/test_scrapers/test_retry.py -v
```

**Step 5: Commit**

```bash
git add backend/app/scrapers/strategies/retry.py backend/tests/test_scrapers/test_retry.py
git commit -m "feat(strategies): add RetryStrategy with exponential backoff"
```

---

## Task 8: Reddit Plugin (Complete Example)

**Files:**
- Create: `backend/app/scrapers/plugins/reddit.py`
- Create: `backend/tests/test_scrapers/test_reddit_plugin.py`

**Step 1: Write test for Reddit plugin**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from app.scrapers.plugins.reddit import RedditScraper

@pytest.mark.asyncio
async def test_reddit_scraper_validate_config():
    scraper = RedditScraper()

    valid_config = {
        "client_id": "test_id",
        "client_secret": "test_secret",
        "subreddits": ["programming"]
    }
    assert scraper.validate_config(valid_config) == True

    invalid_config = {"client_id": "test"}
    assert scraper.validate_config(invalid_config) == False

@pytest.mark.asyncio
async def test_reddit_scraper_returns_articles(monkeypatch):
    scraper = RedditScraper()

    # Mock OAuth2
    async def mock_get_token(self, client_id, secret):
        return "mock_token"

    # Mock fetch posts
    async def mock_fetch_posts(self, subreddit, token, limit):
        return [{
            'title': 'Python Tutorial',
            'url': 'https://example.com',
            'id': '123',
            'published_at': datetime.now(),
            'upvotes': 100,
            'comments_count': 20
        }]

    monkeypatch.setattr(RedditScraper, '_get_access_token', mock_get_token)
    monkeypatch.setattr(RedditScraper, '_fetch_subreddit_posts', mock_fetch_posts)

    config = {
        "client_id": "test",
        "client_secret": "secret",
        "subreddits": ["programming"],
        "max_articles": 10
    }

    articles = await scraper.scrape(config, ["python"])
    assert len(articles) > 0
    assert articles[0]['title'] == 'Python Tutorial'
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_scrapers/test_reddit_plugin.py -v
```

**Step 3: Implement Reddit plugin (partie 1: structure)**

Create: `backend/app/scrapers/plugins/reddit.py`

```python
from typing import List, Dict
from datetime import datetime
import httpx
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.scrapers.strategies.rate_limit import RateLimiter
from app.utils.logger import get_logger

logger = get_logger(__name__)

@scraper_plugin(
    name="reddit",
    display_name="Reddit",
    version="1.0.0",
    required_config=["client_id", "client_secret", "subreddits"]
)
class RedditScraper(ScraperPlugin):

    def __init__(self):
        super().__init__()
        self.rate_limiter = RateLimiter(requests_per_minute=60)
        self.base_url = "https://oauth.reddit.com"

    def validate_config(self, config: Dict) -> bool:
        """Valide la configuration Reddit"""
        required = ['client_id', 'client_secret', 'subreddits']
        return all(k in config for k in required)

    async def scrape(self, config: Dict, keywords: List[str]) -> List[Dict]:
        """Scrape articles depuis Reddit"""
        # 1. Auth OAuth2
        token = await self._get_access_token(
            config['client_id'],
            config['client_secret']
        )

        # 2. Fetch depuis subreddits
        all_articles = []
        subreddits = config.get('subreddits', ['programming'])
        limit = config.get('max_articles', 50)

        for subreddit in subreddits:
            if len(all_articles) >= limit:
                break

            # Fetch posts
            posts = await self._fetch_subreddit_posts(
                subreddit,
                token,
                limit=limit * 2  # Fetch plus pour filtrer
            )

            # Filter + enrich
            for post in posts:
                if len(all_articles) >= limit:
                    break

                # Quick keyword match
                if await self._quick_match(post['title'], keywords):
                    all_articles.append(post)

        return all_articles[:limit]

    async def _get_access_token(self, client_id: str, client_secret: str) -> str:
        """Obtient le token OAuth2"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://www.reddit.com/api/v1/access_token",
                auth=(client_id, client_secret),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": "TechWatch/1.0"}
            )
            response.raise_for_status()
            return response.json()['access_token']

    async def _fetch_subreddit_posts(
        self,
        subreddit: str,
        token: str,
        limit: int
    ) -> List[Dict]:
        """Fetch posts depuis un subreddit"""
        async with self.rate_limiter:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/r/{subreddit}/hot",
                    headers={
                        "Authorization": f"Bearer {token}",
                        "User-Agent": "TechWatch/1.0"
                    },
                    params={"limit": limit}
                )
                response.raise_for_status()

                posts = []
                for post in response.json()['data']['children']:
                    data = post['data']
                    posts.append({
                        'title': data['title'],
                        'url': data['url'],
                        'id': data['id'],
                        'published_at': datetime.fromtimestamp(data['created_utc']),
                        'upvotes': data['ups'],
                        'comments_count': data['num_comments'],
                        'author': data.get('author', 'unknown'),
                        'content': data.get('selftext', ''),
                        'tags': [data.get('link_flair_text')] if data.get('link_flair_text') else []
                    })

                return posts
```

**Step 4: Run tests**

```bash
poetry run pytest tests/test_scrapers/test_reddit_plugin.py -v
```

**Step 5: Commit**

```bash
git add backend/app/scrapers/plugins/reddit.py backend/tests/test_scrapers/test_reddit_plugin.py
git commit -m "feat(scrapers): add Reddit plugin with OAuth2 support"
```

---

## Task 9: HackerNews Plugin

**Files:**
- Create: `backend/app/scrapers/plugins/hackernews.py`
- Create: `backend/tests/test_scrapers/test_hackernews_plugin.py`

**Step 1: Write test**

```python
import pytest
from app.scrapers.plugins.hackernews import HackerNewsScraper

@pytest.mark.asyncio
async def test_hackernews_validate_config():
    scraper = HackerNewsScraper()
    assert scraper.validate_config({"max_articles": 50}) == True

@pytest.mark.asyncio
async def test_hackernews_scrape(monkeypatch):
    scraper = HackerNewsScraper()

    async def mock_fetch_story(self, story_id):
        return {
            'title': 'Show HN: New Python Tool',
            'url': 'https://example.com',
            'by': 'author',
            'time': 1234567890,
            'score': 200,
            'descendants': 50
        }

    async def mock_get_top_stories(self):
        return [1, 2, 3]

    monkeypatch.setattr(HackerNewsScraper, '_fetch_story', mock_fetch_story)
    monkeypatch.setattr(HackerNewsScraper, '_get_top_story_ids', mock_get_top_stories)

    articles = await scraper.scrape({"max_articles": 10}, ["python"])
    assert len(articles) > 0
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_scrapers/test_hackernews_plugin.py -v
```

**Step 3: Implement HackerNews plugin**

Create: `backend/app/scrapers/plugins/hackernews.py`

```python
from typing import List, Dict
from datetime import datetime
import httpx
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.scrapers.strategies.rate_limit import RateLimiter

@scraper_plugin(
    name="hackernews",
    display_name="HackerNews",
    version="1.0.0"
)
class HackerNewsScraper(ScraperPlugin):

    def __init__(self):
        super().__init__()
        self.rate_limiter = RateLimiter(requests_per_minute=120)
        self.base_url = "https://hacker-news.firebaseio.com/v0"

    def validate_config(self, config: Dict) -> bool:
        return True  # Pas de config requise

    async def scrape(self, config: Dict, keywords: List[str]) -> List[Dict]:
        limit = config.get('max_articles', 50)
        story_type = config.get('story_type', 'top')

        # Get story IDs
        story_ids = await self._get_top_story_ids()

        articles = []
        for story_id in story_ids[:limit * 2]:  # Fetch plus pour filtrer
            if len(articles) >= limit:
                break

            story = await self._fetch_story(story_id)
            if not story or 'title' not in story:
                continue

            # Quick keyword match
            if await self._quick_match(story['title'], keywords):
                articles.append({
                    'title': story['title'],
                    'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}"),
                    'published_at': datetime.fromtimestamp(story['time']),
                    'author': story.get('by', 'unknown'),
                    'upvotes': story.get('score', 0),
                    'comments_count': story.get('descendants', 0),
                    'tags': ['hackernews']
                })

        return articles[:limit]

    async def _get_top_story_ids(self) -> List[int]:
        async with self.rate_limiter:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/topstories.json")
                response.raise_for_status()
                return response.json()

    async def _fetch_story(self, story_id: int) -> Dict:
        async with self.rate_limiter:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/item/{story_id}.json")
                response.raise_for_status()
                return response.json()
```

**Step 4: Run tests**

```bash
poetry run pytest tests/test_scrapers/test_hackernews_plugin.py -v
```

**Step 5: Commit**

```bash
git add backend/app/scrapers/plugins/hackernews.py backend/tests/test_scrapers/test_hackernews_plugin.py
git commit -m "feat(scrapers): add HackerNews plugin"
```

---

## Task 10: Save Articles to Database

**Files:**
- Create: `backend/app/scrapers/storage.py`
- Create: `backend/tests/test_scrapers/test_storage.py`

**Step 1: Write test for save_articles**

```python
import pytest
from datetime import datetime
from app.scrapers.storage import save_articles
from app.models.article import Article
from app.database import get_db

@pytest.mark.asyncio
async def test_save_new_article(db_session):
    articles = [{
        'title': 'Test Article',
        'url': 'https://example.com/test',
        'published_at': datetime.now()
    }]

    saved = await save_articles(articles, 'reddit', db_session)
    assert saved == 1

    # Verify in DB
    article = db_session.query(Article).filter_by(url='https://example.com/test').first()
    assert article is not None
    assert article.title == 'Test Article'

@pytest.mark.asyncio
async def test_update_existing_article(db_session):
    # Create initial article
    article = Article(
        title='Original',
        url='https://example.com/dup',
        published_at=datetime.now(),
        source_type='reddit',
        upvotes=10
    )
    db_session.add(article)
    db_session.commit()

    # Update with new data
    articles = [{
        'title': 'Original',
        'url': 'https://example.com/dup',
        'published_at': datetime.now(),
        'upvotes': 50
    }]

    saved = await save_articles(articles, 'reddit', db_session)
    assert saved == 0  # 0 new, 1 updated

    # Verify update
    updated = db_session.query(Article).filter_by(url='https://example.com/dup').first()
    assert updated.upvotes == 50
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_scrapers/test_storage.py -v
```

**Step 3: Implement save_articles**

Create: `backend/app/scrapers/storage.py`

```python
from typing import List, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from pydantic import ValidationError
from app.models.article import Article
from app.schemas.article import ArticleCreate
from app.utils.logger import get_logger

logger = get_logger(__name__)

async def save_articles(
    articles: List[Dict],
    source_type: str,
    db: Session
) -> int:
    """
    Sauvegarde les articles en DB.

    Args:
        articles: Liste de dictionnaires d'articles
        source_type: Type de source ('reddit', 'hackernews', etc.)
        db: Session SQLAlchemy

    Returns:
        Nombre d'articles nouvellement insérés
    """
    saved_count = 0

    for article_data in articles:
        # Validation avec Pydantic
        try:
            validated = ArticleCreate(**article_data)
        except ValidationError as e:
            logger.warning(f"Invalid article data: {e}")
            continue

        # Check si existe (par URL)
        existing = db.query(Article).filter(Article.url == validated.url).first()

        if existing:
            # UPDATE metadata qui peut évoluer
            existing.upvotes = validated.upvotes
            existing.comments_count = validated.comments_count
            existing.tags = validated.tags
            existing.content = validated.content or existing.content
            existing.updated_at = datetime.utcnow()
            logger.debug(f"Updated article: {existing.url}")
        else:
            # INSERT nouveau
            article = Article(
                **validated.dict(),
                source_type=source_type
            )
            db.add(article)
            saved_count += 1
            logger.debug(f"Inserted new article: {article.url}")

    db.commit()
    logger.info(f"Saved {saved_count} new articles from {source_type}")

    return saved_count
```

**Step 4: Run tests**

```bash
poetry run pytest tests/test_scrapers/test_storage.py -v
```

**Step 5: Commit**

```bash
git add backend/app/scrapers/storage.py backend/tests/test_scrapers/test_storage.py
git commit -m "feat(scrapers): add save_articles with deduplication"
```

---

## Task 11: Celery Orchestration Task

**Files:**
- Create: `backend/app/tasks/scraping.py`
- Create: `backend/tests/test_tasks/test_scraping.py`

**Step 1: Write test for scrape_all_sources**

```python
import pytest
from unittest.mock import AsyncMock, patch
from app.tasks.scraping import scrape_all_sources

@pytest.mark.asyncio
async def test_scrape_all_sources_loads_active_sources(db_session):
    # Setup
    from app.models.source import Source
    source = Source(
        name="Reddit",
        type="reddit",
        is_active=True,
        config={"subreddits": ["programming"], "max_articles": 10}
    )
    db_session.add(source)
    db_session.commit()

    with patch('app.tasks.scraping.scrape_single_source') as mock_scrape:
        mock_scrape.return_value = {"source": "reddit", "scraped": 10, "saved": 5}

        result = await scrape_all_sources()

        assert mock_scrape.called
        assert "reddit" in [call[0][0] for call in mock_scrape.call_args_list]
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_tasks/test_scraping.py -v
```

**Step 3: Implement scrape_all_sources (partie 1)**

Create: `backend/app/tasks/scraping.py`

```python
import asyncio
from typing import List, Dict, Optional
from celery import shared_task
from app.database import SessionLocal
from app.models.source import Source
from app.models.keyword import Keyword
from app.scrapers.registry import ScraperRegistry
from app.scrapers.storage import save_articles
from app.scrapers.strategies.rate_limit import RateLimiter
from app.scrapers.strategies.retry import RetryStrategy, MaxRetriesExceeded
from app.utils.logger import get_logger

logger = get_logger(__name__)

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Divise une liste en chunks"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

@shared_task(name="scrape_all_sources")
def scrape_all_sources(
    sources: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None
):
    """
    Tâche Celery pour scraper toutes les sources actives.

    Args:
        sources: Liste des sources à scraper (None = toutes actives)
        keywords: Liste des keywords (None = tous actifs)

    Returns:
        Résumé des résultats
    """
    return asyncio.run(_scrape_all_sources_async(sources, keywords))

async def _scrape_all_sources_async(
    sources: Optional[List[str]],
    keywords: Optional[List[str]]
) -> Dict:
    """Version async de scrape_all_sources"""
    db = SessionLocal()

    try:
        # 1. Récupérer sources actives
        query = db.query(Source).filter(Source.is_active == True)
        if sources:
            query = query.filter(Source.type.in_(sources))
        active_sources = query.all()

        logger.info(f"Scraping {len(active_sources)} active sources")

        # 2. Charger keywords
        if not keywords:
            keywords = [kw.keyword for kw in db.query(Keyword).filter(Keyword.is_active == True).all()]

        logger.info(f"Using {len(keywords)} keywords")

        # 3. Grouper en batches de 3 pour exécution semi-parallèle
        batches = chunk_list(active_sources, batch_size=3)

        all_results = []

        # 4. Exécuter batch par batch
        for batch_idx, batch in enumerate(batches):
            logger.info(f"Processing batch {batch_idx + 1}/{len(batches)}")

            tasks = [
                scrape_single_source(source.type, source.config, keywords, db)
                for source in batch
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)
            all_results.extend(results)

        return {
            "total_sources": len(active_sources),
            "results": all_results
        }

    finally:
        db.close()

async def scrape_single_source(
    source_type: str,
    config: Dict,
    keywords: List[str],
    db
) -> Dict:
    """
    Scrape une source unique.

    Args:
        source_type: Type de source ('reddit', 'hackernews', etc.)
        config: Configuration de la source
        keywords: Keywords pour filtrage
        db: Session DB

    Returns:
        Résultat du scraping
    """
    logger.info(f"Starting scraping for {source_type}")

    try:
        # 1. Récupérer plugin
        registry = ScraperRegistry()
        scraper = registry.get(source_type)

        if not scraper:
            return {"source": source_type, "error": "Scraper not found"}

        # 2. Initialiser strategies
        rate_limiter = RateLimiter(config.get('rate_limit', 60))
        retry_strategy = RetryStrategy(max_retries=3, backoff_factor=2)

        # 3. Scraper avec retry
        try:
            articles = await retry_strategy.execute(
                scraper.scrape(config, keywords)
            )

            # 4. Sauvegarder en DB
            saved_count = await save_articles(articles, source_type, db)

            # 5. Update last_scraped_at
            source = db.query(Source).filter(Source.type == source_type).first()
            if source:
                from datetime import datetime
                source.last_scraped_at = datetime.utcnow()
                db.commit()

            logger.info(f"Successfully scraped {source_type}: {len(articles)} articles, {saved_count} new")

            return {
                "source": source_type,
                "scraped": len(articles),
                "saved": saved_count,
                "status": "success"
            }

        except MaxRetriesExceeded as e:
            logger.error(f"Failed to scrape {source_type} after retries: {e}")
            return {"source": source_type, "error": str(e), "status": "failed"}

    except Exception as e:
        logger.exception(f"Unexpected error scraping {source_type}: {e}")
        return {"source": source_type, "error": str(e), "status": "failed"}
```

**Step 4: Run tests**

```bash
poetry run pytest tests/test_tasks/test_scraping.py -v
```

**Step 5: Commit**

```bash
git add backend/app/tasks/scraping.py backend/tests/test_tasks/test_scraping.py
git commit -m "feat(tasks): add Celery scraping orchestration task"
```

---

## Task 12: API Endpoints

**Files:**
- Create: `backend/app/api/scraping.py`
- Create: `backend/tests/test_api/test_scraping.py`

**Step 1: Write test for API endpoints**

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_trigger_scraping():
    response = client.post("/api/scraping/trigger")
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert "status_url" in data

def test_trigger_scraping_with_sources():
    response = client.post(
        "/api/scraping/trigger",
        json={"sources": ["reddit"], "keywords": ["python"]}
    )
    assert response.status_code == 200

def test_get_scraping_status():
    # First trigger
    trigger_response = client.post("/api/scraping/trigger")
    task_id = trigger_response.json()["task_id"]

    # Then check status
    status_response = client.get(f"/api/scraping/status/{task_id}")
    assert status_response.status_code == 200
    data = status_response.json()
    assert "status" in data
    assert data["task_id"] == task_id
```

**Step 2: Run test to verify it fails**

```bash
poetry run pytest tests/test_api/test_scraping.py -v
```

**Step 3: Implement API endpoints**

Create: `backend/app/api/scraping.py`

```python
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from celery.result import AsyncResult
from app.database import get_db
from app.models.source import Source
from app.tasks.scraping import scrape_all_sources
from app.tasks.celery_app import celery_app

router = APIRouter(prefix="/scraping", tags=["scraping"])

@router.post("/trigger")
async def trigger_scraping(
    sources: Optional[List[str]] = None,
    keywords: Optional[List[str]] = None,
    db: Session = Depends(get_db)
):
    """
    Déclenche le scraping manuellement.

    Args:
        sources: Liste des sources à scraper (None = toutes actives)
        keywords: Liste des keywords (None = tous actifs)

    Returns:
        Task ID pour suivre la progression
    """
    # Validation des sources si fournies
    if sources:
        valid_sources = [s.type for s in db.query(Source.type).filter(Source.type.in_(sources)).all()]
        if len(valid_sources) != len(sources):
            invalid = set(sources) - set(valid_sources)
            raise HTTPException(400, f"Invalid source(s): {invalid}")

    # Lancer la tâche Celery
    task = scrape_all_sources.delay(sources=sources, keywords=keywords)

    return {
        "message": "Scraping started",
        "task_id": task.id,
        "status_url": f"/api/scraping/status/{task.id}"
    }

@router.get("/status/{task_id}")
async def get_scraping_status(task_id: str):
    """
    Récupère le statut d'une tâche de scraping.

    Args:
        task_id: ID de la tâche Celery

    Returns:
        Statut et résultat si terminé
    """
    task = AsyncResult(task_id, app=celery_app)

    response = {
        "task_id": task_id,
        "status": task.state,
    }

    if task.ready():
        response["result"] = task.result
    elif task.failed():
        response["error"] = str(task.info)

    return response
```

**Step 4: Register router in main.py**

Modify: `backend/app/main.py`

```python
from app.api import scraping

app.include_router(scraping.router, prefix="/api")
```

**Step 5: Run tests**

```bash
poetry run pytest tests/test_api/test_scraping.py -v
```

**Step 6: Commit**

```bash
git add backend/app/api/scraping.py backend/tests/test_api/test_scraping.py backend/app/main.py
git commit -m "feat(api): add scraping trigger and status endpoints"
```

---

## Task 13: Celery Beat Configuration

**Files:**
- Modify: `backend/app/tasks/celery_app.py`

**Step 1: Configure Celery Beat schedule**

```python
from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "techwatch",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

# Celery Beat Schedule
celery_app.conf.beat_schedule = {
    'scrape-all-sources-every-6h': {
        'task': 'scrape_all_sources',
        'schedule': crontab(hour='*/6'),  # Toutes les 6 heures
        'kwargs': {
            'sources': None,  # Toutes les sources actives
            'keywords': None  # Tous les keywords actifs
        }
    },
}
```

**Step 2: Test Celery configuration**

```bash
cd backend
poetry run celery -A app.tasks.celery_app inspect registered
```

Expected: Liste des tâches enregistrées incluant `scrape_all_sources`

**Step 3: Commit**

```bash
git add backend/app/tasks/celery_app.py
git commit -m "feat(celery): configure Beat schedule for automatic scraping"
```

---

## Task 14: Seed Initial Sources

**Files:**
- Create: `backend/scripts/seed_sources.py`

**Step 1: Create seed script**

```python
from app.database import SessionLocal
from app.models.source import Source

def seed_sources():
    """Seed initial sources configuration"""
    db = SessionLocal()

    sources = [
        {
            "name": "Reddit",
            "type": "reddit",
            "base_url": "https://oauth.reddit.com",
            "is_active": True,
            "config": {
                "client_id": "env:REDDIT_CLIENT_ID",
                "client_secret": "env:REDDIT_CLIENT_SECRET",
                "subreddits": ["programming", "python", "technology", "devops"],
                "max_articles": 100,
                "rate_limit": 60
            }
        },
        {
            "name": "HackerNews",
            "type": "hackernews",
            "base_url": "https://hacker-news.firebaseio.com/v0",
            "is_active": True,
            "config": {
                "max_articles": 50,
                "story_type": "top",
                "rate_limit": 120
            }
        },
        {
            "name": "Dev.to",
            "type": "devto",
            "base_url": "https://dev.to/api",
            "is_active": True,
            "config": {
                "max_articles": 50,
                "tags": ["python", "javascript", "webdev"],
                "rate_limit": 60
            }
        }
    ]

    for source_data in sources:
        existing = db.query(Source).filter(Source.type == source_data["type"]).first()
        if not existing:
            source = Source(**source_data)
            db.add(source)
            print(f"Added source: {source_data['name']}")
        else:
            print(f"Source already exists: {source_data['name']}")

    db.commit()
    db.close()
    print("Sources seeded successfully")

if __name__ == "__main__":
    seed_sources()
```

**Step 2: Run seed script**

```bash
poetry run python backend/scripts/seed_sources.py
```

**Step 3: Commit**

```bash
git add backend/scripts/seed_sources.py
git commit -m "feat(scripts): add source seeding script"
```

---

## Task 15: Integration Tests

**Files:**
- Create: `backend/tests/integration/test_full_scraping_flow.py`

**Step 1: Write integration test**

```python
import pytest
from app.tasks.scraping import scrape_all_sources
from app.models.source import Source
from app.models.keyword import Keyword
from app.models.article import Article

@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_scraping_flow(db_session):
    """Test complet: source -> scraping -> save DB"""

    # Setup source
    source = Source(
        name="Reddit Test",
        type="reddit",
        is_active=True,
        config={
            "client_id": "test_id",
            "client_secret": "test_secret",
            "subreddits": ["programming"],
            "max_articles": 5
        }
    )
    db_session.add(source)

    # Setup keywords
    keyword = Keyword(keyword="python", is_active=True, weight=1.0)
    db_session.add(keyword)

    db_session.commit()

    # Execute scraping (with mocks for external APIs)
    # ... test with mocked httpx responses

    # Verify articles in DB
    articles = db_session.query(Article).all()
    assert len(articles) > 0
```

**Step 2: Run integration tests**

```bash
poetry run pytest tests/integration/ -v -m integration
```

**Step 3: Commit**

```bash
git add backend/tests/integration/
git commit -m "test(integration): add full scraping flow test"
```

---

## Task 16: Documentation

**Files:**
- Create: `backend/docs/SCRAPING_SYSTEM.md`

**Step 1: Write comprehensive documentation**

Include:
- Architecture overview
- How to add a new scraper plugin
- Configuration guide
- API usage examples
- Troubleshooting

**Step 2: Commit**

```bash
git add backend/docs/SCRAPING_SYSTEM.md
git commit -m "docs: add scraping system documentation"
```

---

## Summary

**Implementation complète en 16 tâches:**

1. ✅ Database migrations (sources, scraping_runs)
2. ✅ SQLAlchemy models
3. ✅ Pydantic schemas
4. ✅ Base ScraperPlugin interface
5. ✅ Plugin registry avec auto-discovery
6. ✅ RateLimiter strategy
7. ✅ RetryStrategy
8. ✅ Reddit plugin (exemple complet)
9. ✅ HackerNews plugin
10. ✅ Save articles to database
11. ✅ Celery orchestration task
12. ✅ API endpoints (trigger, status)
13. ✅ Celery Beat configuration
14. ✅ Seed initial sources
15. ✅ Integration tests
16. ✅ Documentation

**Plugins restants (similaires à Reddit/HN):**
- Dev.to (API REST simple)
- GitHub Trending (HTML scraping avec BeautifulSoup)
- Medium (RSS parsing avec feedparser)

**Prochaines étapes après implémentation:**
- Ajouter les 3 plugins restants (Dev.to, GitHub, Medium)
- Tests end-to-end avec vrais APIs (en staging)
- Monitoring et alerting (Sentry, Prometheus)
- Rate limit adaptatif basé sur les quotas restants
- Dashboard admin pour gérer les sources

**Métriques de succès:**
- ✅ Coverage >85%
- ✅ Scraping complet <5min
- ✅ Taux d'échec <5%
- ✅ Nouveau plugin en <2h
