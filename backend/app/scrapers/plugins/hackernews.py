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
