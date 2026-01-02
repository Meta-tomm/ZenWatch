from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import asyncio
import httpx
import hashlib
import json
import random
from redis.asyncio import Redis
from app.schemas.scraped_article import ScrapedArticle
from app.utils.logger import get_logger


class ScraperPlugin(ABC):
    """
    Base class for all scrapers with retry logic, caching, and error handling

    Subclasses must implement:
    - scrape(): Main scraping logic
    - validate_config(): Config validation

    Features:
    - Automatic retries with exponential backoff + jitter
    - Redis caching with configurable TTL
    - Shared HTTP client with proper lifecycle
    - Best-effort error handling
    """

    # Metadata (set by @scraper_plugin decorator)
    name: str
    display_name: str
    version: str

    # Configuration (override in subclasses if needed)
    MAX_RETRIES: int = 3
    CACHE_TTL: int = 3600  # 1 hour
    TIMEOUT: float = 30.0

    def __init__(self, redis_client: Optional[Redis] = None):
        self.client: Optional[httpx.AsyncClient] = None
        self.redis = redis_client
        self.logger = get_logger(self.__class__.__name__)

    @abstractmethod
    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape articles from source

        Args:
            config: Source-specific configuration from database
            keywords: List of keywords for filtering

        Returns:
            List of validated ScrapedArticle objects
        """
        pass

    @abstractmethod
    def validate_config(self, config: Dict) -> bool:
        """
        Validate scraper configuration

        Args:
            config: Configuration to validate

        Returns:
            True if valid, False otherwise
        """
        pass

    async def scrape_with_cache(
        self,
        config: Dict,
        keywords: List[str]
    ) -> List[ScrapedArticle]:
        """
        Scrape with Redis caching

        Checks cache first, falls back to scraping if cache miss
        """
        cache_key = self._make_cache_key(keywords, config)

        # Try cache first
        cached_data = await self._get_cached(cache_key)
        if cached_data:
            return [ScrapedArticle(**item) for item in cached_data]

        # Cache miss - scrape fresh data
        self.logger.info(f"Cache miss for {cache_key}, fetching fresh data")
        articles = await self.scrape(config, keywords)

        # Cache the results
        article_dicts = [article.model_dump(mode='json') for article in articles]
        await self._set_cached(cache_key, article_dicts)

        return articles

    async def _retry_request(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Execute HTTP request with smart retry logic

        Retry strategy:
        - 429 (rate limit): Always retry with 2x backoff
        - 500/502/503/504 (server errors): Retry with backoff
        - 4xx (client errors): No retry, fail immediately
        - Network errors: Retry with backoff
        """
        last_exception = None

        for attempt in range(self.MAX_RETRIES):
            try:
                response = await self.client.request(method, url, **kwargs)

                # Success or client error (don't retry 4xx except 429)
                if response.status_code < 500 and response.status_code != 429:
                    response.raise_for_status()
                    return response

                # Server error or rate limit - retry
                if attempt < self.MAX_RETRIES - 1:
                    delay = self._calculate_backoff(attempt, response.status_code)
                    self.logger.warning(
                        f"Request failed with {response.status_code}, "
                        f"retrying in {delay:.2f}s (attempt {attempt + 1}/{self.MAX_RETRIES})"
                    )
                    await asyncio.sleep(delay)
                else:
                    response.raise_for_status()

            except httpx.RequestError as e:
                last_exception = e
                if attempt < self.MAX_RETRIES - 1:
                    delay = self._calculate_backoff(attempt)
                    self.logger.warning(
                        f"Network error: {e}, retrying in {delay:.2f}s "
                        f"(attempt {attempt + 1}/{self.MAX_RETRIES})"
                    )
                    await asyncio.sleep(delay)

        # All retries exhausted
        raise last_exception or httpx.HTTPError(f"Failed after {self.MAX_RETRIES} attempts")

    def _calculate_backoff(self, attempt: int, status_code: Optional[int] = None) -> float:
        """
        Exponential backoff with jitter

        Base delay: 2^attempt seconds
        Jitter: ±25% randomization to prevent thundering herd
        Special case: 429 (rate limit) gets 2x longer delays
        """
        base_delay = 2 ** attempt  # 1s, 2s, 4s, 8s...

        # Longer delays for rate limiting
        if status_code == 429:
            base_delay *= 2

        # Add jitter: ±25%
        jitter = random.uniform(0.75, 1.25)

        return base_delay * jitter

    async def _get_cached(self, cache_key: str) -> Optional[List[dict]]:
        """Get cached scraper results from Redis"""
        if not self.redis:
            return None

        try:
            cached = await self.redis.get(cache_key)
            if cached:
                self.logger.info(f"Cache hit for {cache_key}")
                return json.loads(cached)
        except Exception as e:
            self.logger.warning(f"Cache read error: {e}")

        return None

    async def _set_cached(self, cache_key: str, data: List[dict]) -> None:
        """Store scraper results in Redis with TTL"""
        if not self.redis:
            return

        try:
            await self.redis.setex(
                cache_key,
                self.CACHE_TTL,
                json.dumps(data, default=str)  # default=str handles datetime
            )
            self.logger.info(f"Cached {len(data)} articles for {self.CACHE_TTL}s")
        except Exception as e:
            self.logger.warning(f"Cache write error: {e}")

    def _make_cache_key(self, keywords: List[str], config: Dict) -> str:
        """
        Generate unique cache key based on scraper and params

        Format: scraper:{name}:{hash(keywords+config)}
        """
        params = f"{sorted(keywords)}:{sorted(config.items())}"
        params_hash = hashlib.md5(params.encode()).hexdigest()[:8]

        return f"scraper:{self.name}:{params_hash}"

    async def _quick_match(self, title: str, keywords: List[str]) -> bool:
        """
        Quick keyword match on title (case-insensitive)

        Args:
            title: Article title
            keywords: List of keywords

        Returns:
            True if at least one keyword is present (or if no keywords)
        """
        if not keywords:
            return True  # No filtering if no keywords
        title_lower = title.lower()
        return any(kw.lower() in title_lower for kw in keywords)

    async def __aenter__(self):
        """Context manager for httpx.AsyncClient"""
        self.client = httpx.AsyncClient(
            timeout=self.TIMEOUT,
            headers={"User-Agent": "TechWatch/1.0 (Educational Project)"}
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close HTTP client"""
        if self.client:
            await self.client.aclose()
