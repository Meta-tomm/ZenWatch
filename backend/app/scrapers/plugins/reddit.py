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
                        'external_id': data['id'],
                        'published_at': datetime.fromtimestamp(data['created_utc']),
                        'upvotes': data['ups'],
                        'comments_count': data['num_comments'],
                        'author': data.get('author', 'unknown'),
                        'content': data.get('selftext', ''),
                        'tags': [data.get('link_flair_text')] if data.get('link_flair_text') else []
                    })

                return posts
