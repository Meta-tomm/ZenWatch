from typing import List, Dict
from datetime import datetime
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.scrapers.strategies.rate_limit import RateLimiter
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="devto",
    display_name="Dev.to",
    version="1.0.0"
)
class DevToScraper(ScraperPlugin):
    """
    Dev.to scraper using Forem REST API

    API docs: https://developers.forem.com/api
    Rate limit: ~10 req/30s (unofficial, conservative estimate)

    Features:
    - Fetches latest/top articles from Dev.to
    - Filters by tags (Dev.to's keyword system)
    - Returns validated Pydantic models
    - Best-effort error handling
    """

    # Configuration
    MAX_RETRIES = 3
    CACHE_TTL = 1800  # 30 minutes
    TIMEOUT = 30.0

    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        self.rate_limiter = RateLimiter(requests_per_minute=20)
        self.base_url = "https://dev.to/api"

    def validate_config(self, config: Dict) -> bool:
        """No special config required for Dev.to"""
        return True

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape articles from Dev.to

        Strategy:
        1. If keywords provided, search by tags (Dev.to's tag system)
        2. Otherwise fetch latest articles
        3. Parse and validate each article
        4. Return up to max_articles
        """
        max_articles = config.get('max_articles', 50)
        per_page = min(max_articles, 100)  # API max is 1000, but keep it reasonable

        self.logger.info(f"Fetching Dev.to articles for keywords: {keywords}")

        articles = []
        errors = 0

        if keywords:
            # Search by tags (Dev.to uses tags as their keyword system)
            for keyword in keywords[:5]:  # Limit to 5 keywords to avoid too many requests
                try:
                    keyword_articles = await self._fetch_by_tag(keyword, per_page)
                    articles.extend(keyword_articles)

                    if len(articles) >= max_articles:
                        break

                except Exception as e:
                    errors += 1
                    self.logger.warning(f"Failed to fetch articles for tag '{keyword}': {e}")
                    continue
        else:
            # Fetch latest articles
            try:
                articles = await self._fetch_latest(per_page)
            except Exception as e:
                self.logger.error(f"Failed to fetch latest articles: {e}")
                return []

        # Remove duplicates by URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        # Limit to max_articles
        result = unique_articles[:max_articles]

        self.logger.info(
            f"Fetched {len(result)} Dev.to articles "
            f"({errors} errors, {len(articles) - len(result)} duplicates removed)"
        )

        return result

    async def _fetch_latest(self, per_page: int = 50) -> List[ScrapedArticle]:
        """Fetch latest articles from Dev.to"""
        async with self.rate_limiter:
            url = f"{self.base_url}/articles"
            params = {
                'per_page': per_page,
                'state': 'fresh'  # Get fresh/recent articles
            }

            response = await self._retry_request('GET', url, params=params)
            data = response.json()

        return [self._parse_article(article) for article in data if self._parse_article(article)]

    async def _fetch_by_tag(self, tag: str, per_page: int = 50) -> List[ScrapedArticle]:
        """Fetch articles by tag"""
        async with self.rate_limiter:
            url = f"{self.base_url}/articles"
            params = {
                'tag': tag.lower().replace(' ', ''),  # Dev.to tags are lowercase, no spaces
                'per_page': per_page,
                'state': 'fresh'
            }

            response = await self._retry_request('GET', url, params=params)
            data = response.json()

        return [self._parse_article(article) for article in data if self._parse_article(article)]

    def _parse_article(self, data: Dict) -> ScrapedArticle | None:
        """
        Parse Dev.to article data to ScrapedArticle

        Returns None if required fields are missing or validation fails
        """
        try:
            # Extract required fields
            title = data.get('title')
            url = data.get('url')
            article_id = data.get('id')

            if not all([title, url, article_id]):
                return None

            # Parse published date
            published_str = data.get('published_at') or data.get('created_at')
            if published_str:
                # Dev.to returns ISO 8601 format
                published_at = datetime.fromisoformat(published_str.replace('Z', '+00:00'))
            else:
                published_at = datetime.now()

            # Extract author info
            user = data.get('user', {})
            author = user.get('name') or user.get('username') or 'unknown'

            # Get tags (Dev.to's tag_list is already an array of strings)
            tags = data.get('tag_list', [])

            # Create and validate with Pydantic
            return ScrapedArticle(
                title=title,
                url=url,
                source_type='devto',
                external_id=str(article_id),
                content=data.get('description'),  # Short description, not full content
                author=author,
                published_at=published_at,
                tags=tags,
                upvotes=data.get('positive_reactions_count', 0),
                comments_count=data.get('comments_count', 0),
                raw_data=data
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse Dev.to article: {e}")
            return None
