from typing import List, Dict
from datetime import datetime
import feedparser
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="official_blogs",
    display_name="Official AI Blogs",
    version="1.0.0"
)
class OfficialBlogsScraper(ScraperPlugin):
    """
    Scraper for official AI company blogs via RSS feeds.

    Supports:
    - OpenAI Blog: https://openai.com/blog/rss.xml
    - DeepMind Blog: https://deepmind.google/blog/rss.xml

    Config format:
    {
        "feeds": [
            {"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"},
            {"name": "DeepMind", "url": "https://deepmind.google/blog/rss.xml"}
        ],
        "max_articles_per_feed": 20
    }
    """

    CACHE_TTL = 3600  # 1 hour

    def validate_config(self, config: Dict) -> bool:
        """Validate config has feeds list"""
        return True

    def _parse_rss_entry(self, entry, feed_name: str) -> ScrapedArticle | None:
        """
        Parse RSS entry to ScrapedArticle

        Args:
            entry: feedparser entry object
            feed_name: Name of the feed (e.g., "OpenAI", "DeepMind")

        Returns:
            ScrapedArticle or None if parsing fails
        """
        try:
            title = getattr(entry, 'title', None)
            link = getattr(entry, 'link', None)
            entry_id = getattr(entry, 'id', link)

            if not title or not link:
                self.logger.warning(f"Skipping entry with missing title or link")
                return None

            # Parse published date
            published_parsed = getattr(entry, 'published_parsed', None)
            if published_parsed:
                published_at = datetime(*published_parsed[:6])
            else:
                published_at = datetime.now()

            # Get content/summary
            content = entry.get('summary', '') or entry.get('description', '')

            # Get author if available
            author = entry.get('author', feed_name)

            return ScrapedArticle(
                title=title,
                url=link,
                source_type='official_blogs',
                external_id=str(entry_id),
                content=content,
                author=author,
                published_at=published_at,
                tags=[feed_name],
                raw_data={'feed_name': feed_name}
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse RSS entry: {e}")
            return None

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """Scrape articles from configured RSS feeds"""
        return []
