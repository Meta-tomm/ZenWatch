from typing import List, Dict, Optional
from datetime import datetime, timedelta
import httpx
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.scrapers.strategies.rate_limit import RateLimiter
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="reddit",
    display_name="Reddit",
    version="2.0.0",
    required_config=["client_id", "client_secret"]
)
class RedditScraper(ScraperPlugin):
    """
    Reddit scraper using OAuth2 API

    API docs: https://www.reddit.com/dev/api
    Rate limit: 60 req/min (OAuth2)

    Features:
    - OAuth2 authentication with token caching
    - Searches multiple subreddits
    - Filters by keywords in title/selftext
    - Returns validated Pydantic models
    - Best-effort error handling
    """

    # Configuration
    MAX_RETRIES = 3
    CACHE_TTL = 1800  # 30 minutes for articles
    TIMEOUT = 30.0

    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        self.rate_limiter = RateLimiter(requests_per_minute=60)
        self.base_url = "https://oauth.reddit.com"
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None

    def validate_config(self, config: Dict) -> bool:
        """Validate Reddit configuration"""
        required = ['client_id', 'client_secret']
        return all(k in config for k in required)

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape articles from Reddit

        Strategy:
        1. Authenticate with OAuth2 (cached token)
        2. Fetch posts from specified subreddits (or defaults)
        3. Filter by keywords in title/selftext
        4. Parse and validate with Pydantic
        5. Return up to max_articles
        """
        max_articles = config.get('max_articles', 50)
        subreddits = config.get('subreddits', ['programming', 'technology', 'python'])

        self.logger.info(f"Fetching Reddit articles from r/{', r/'.join(subreddits)}")

        # Get OAuth2 token (cached if still valid)
        token = await self._get_access_token(
            config['client_id'],
            config['client_secret']
        )

        articles = []
        errors = 0

        # Fetch from each subreddit
        for subreddit in subreddits:
            if len(articles) >= max_articles:
                break

            try:
                subreddit_articles = await self._fetch_subreddit(
                    subreddit,
                    token,
                    keywords,
                    limit=max_articles
                )
                articles.extend(subreddit_articles)

            except Exception as e:
                errors += 1
                self.logger.warning(f"Failed to fetch from r/{subreddit}: {e}")
                continue

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
            f"Fetched {len(result)} Reddit articles "
            f"({errors} subreddit errors, {len(articles) - len(result)} duplicates removed)"
        )

        return result

    async def _get_access_token(self, client_id: str, client_secret: str) -> str:
        """
        Get OAuth2 access token with caching

        Token is cached in memory for 1 hour (Reddit tokens expire after 1h)
        """
        # Check if cached token is still valid
        if self._access_token and self._token_expires_at:
            if datetime.now() < self._token_expires_at:
                self.logger.debug("Using cached Reddit OAuth token")
                return self._access_token

        # Get new token
        self.logger.info("Fetching new Reddit OAuth token")

        async with self.rate_limiter:
            response = await self._retry_request(
                'POST',
                "https://www.reddit.com/api/v1/access_token",
                auth=(client_id, client_secret),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": "TechWatch/1.0 (Educational Project)"}
            )

            data = response.json()
            self._access_token = data['access_token']

            # Reddit tokens expire in 3600s (1 hour), cache for 55 min to be safe
            self._token_expires_at = datetime.now() + timedelta(minutes=55)

            return self._access_token

    async def _fetch_subreddit(
        self,
        subreddit: str,
        token: str,
        keywords: List[str],
        limit: int = 50
    ) -> List[ScrapedArticle]:
        """
        Fetch posts from a subreddit

        Fetches 'hot' posts and filters by keywords
        """
        async with self.rate_limiter:
            url = f"{self.base_url}/r/{subreddit}/hot"
            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": "TechWatch/1.0 (Educational Project)"
            }
            params = {"limit": min(limit * 2, 100)}  # Reddit max is 100

            response = await self._retry_request('GET', url, headers=headers, params=params)
            data = response.json()

        articles = []

        for post in data.get('data', {}).get('children', []):
            try:
                article = self._parse_post(post['data'], subreddit, keywords)
                if article:  # None if keywords don't match
                    articles.append(article)

            except Exception as e:
                self.logger.warning(f"Failed to parse Reddit post: {e}")
                continue

        return articles

    def _parse_post(
        self,
        data: Dict,
        subreddit: str,
        keywords: List[str]
    ) -> ScrapedArticle | None:
        """
        Parse Reddit post to ScrapedArticle

        Returns None if:
        - Keywords don't match
        - Required fields missing
        - Validation fails
        """
        try:
            title = data.get('title', '')
            url = data.get('url', '')
            selftext = data.get('selftext', '')

            # Filter by keywords (check title and selftext)
            text_to_search = f"{title} {selftext}".lower()
            if keywords:
                if not any(kw.lower() in text_to_search for kw in keywords):
                    return None

            # Build tags from flair and subreddit
            tags = [subreddit]
            if data.get('link_flair_text'):
                tags.append(data['link_flair_text'])

            # Create and validate with Pydantic
            return ScrapedArticle(
                title=title,
                url=url,
                source_type='reddit',
                external_id=data.get('id', ''),
                content=selftext if selftext else None,
                author=data.get('author', 'unknown'),
                published_at=datetime.fromtimestamp(data.get('created_utc', 0)),
                tags=tags,
                upvotes=data.get('ups', 0),
                comments_count=data.get('num_comments', 0),
                raw_data=data
            )

        except Exception as e:
            self.logger.warning(f"Failed to create ScrapedArticle from Reddit post: {e}")
            return None
