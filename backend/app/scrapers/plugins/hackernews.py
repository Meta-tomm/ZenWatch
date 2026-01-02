from typing import List, Dict
from datetime import datetime
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.scrapers.strategies.rate_limit import RateLimiter
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="hackernews",
    display_name="HackerNews",
    version="2.0.0"
)
class HackerNewsScraper(ScraperPlugin):
    """
    HackerNews scraper using Firebase API

    API docs: https://github.com/HackerNews/API
    Rate limit: ~100 req/min (unofficial, conservative estimate)

    Features:
    - Fetches top stories from HN
    - Filters by keywords in title
    - Returns validated Pydantic models
    - Best-effort error handling (skips invalid stories)
    """

    # Configuration
    MAX_RETRIES = 3
    CACHE_TTL = 1800  # 30 minutes
    TIMEOUT = 30.0

    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        self.rate_limiter = RateLimiter(requests_per_minute=100)
        self.base_url = "https://hacker-news.firebaseio.com/v0"

    def validate_config(self, config: Dict) -> bool:
        """No config required for HackerNews"""
        return True

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape top stories from HackerNews

        Strategy:
        1. Get top 500 story IDs
        2. Fetch each story's details
        3. Filter by keywords in title
        4. Parse and validate
        5. Return up to max_articles matches
        """
        max_articles = config.get('max_articles', 50)

        self.logger.info(f"Fetching HN articles for keywords: {keywords}")

        # Get top story IDs
        story_ids = await self._get_top_story_ids()

        articles = []
        errors = 0

        # Fetch stories until we have enough matches
        for story_id in story_ids[:500]:  # Process top 500
            if len(articles) >= max_articles:
                break

            try:
                article = await self._fetch_and_parse_story(story_id, keywords)
                if article:  # None if keywords don't match or invalid
                    articles.append(article)

            except Exception as e:
                errors += 1
                self.logger.warning(f"Failed to parse story {story_id}: {e}")
                # Best effort: continue to next article
                continue

        self.logger.info(
            f"Fetched {len(articles)} HN articles "
            f"({errors} errors skipped)"
        )

        return articles

    async def _get_top_story_ids(self) -> List[int]:
        """Get list of top story IDs from HN"""
        async with self.rate_limiter:
            url = f"{self.base_url}/topstories.json"
            response = await self._retry_request('GET', url)
            return response.json()

    async def _fetch_and_parse_story(
        self,
        story_id: int,
        keywords: List[str]
    ) -> ScrapedArticle | None:
        """
        Fetch story details and parse to ScrapedArticle

        Returns None if:
        - Keywords don't match title
        - Story is deleted
        - Story is not a "story" type (job, poll, etc.)
        - Required fields missing
        """
        async with self.rate_limiter:
            url = f"{self.base_url}/item/{story_id}.json"
            response = await self._retry_request('GET', url)
            data = response.json()

        # Skip if not a story or deleted
        if not data or data.get('type') != 'story' or data.get('deleted'):
            return None

        title = data.get('title', '')
        if not title:
            return None

        # Filter by keywords (case-insensitive)
        if not await self._quick_match(title, keywords):
            return None

        # Get URL (use HN discussion URL if no external link)
        url = data.get('url')
        if not url:
            url = f"https://news.ycombinator.com/item?id={story_id}"

        # Parse and validate with Pydantic
        try:
            return ScrapedArticle(
                title=title,
                url=url,
                source_type='hackernews',
                external_id=str(story_id),
                content=data.get('text'),  # May be None for link posts
                author=data.get('by'),
                published_at=datetime.fromtimestamp(data.get('time', 0)),
                tags=[],  # HN doesn't have tags
                upvotes=data.get('score', 0),
                comments_count=data.get('descendants', 0),
                raw_data=data  # Store original for debugging
            )
        except Exception as e:
            self.logger.warning(f"Failed to create ScrapedArticle for story {story_id}: {e}")
            return None
