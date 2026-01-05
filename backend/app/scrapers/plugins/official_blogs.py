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
        """
        Scrape articles from configured RSS feeds

        Args:
            config: Configuration with feeds list
            keywords: Optional list of keywords for filtering

        Returns:
            List of ScrapedArticle objects
        """
        feeds = config.get('feeds', self._get_default_feeds())
        max_per_feed = config.get('max_articles_per_feed', 20)

        if not feeds:
            self.logger.info("No feeds configured, returning empty list")
            return []

        articles = []
        errors = 0

        for feed_config in feeds:
            feed_name = feed_config.get('name', 'Unknown')
            feed_url = feed_config.get('url')

            if not feed_url:
                self.logger.warning(f"Skipping feed {feed_name}: no URL")
                continue

            try:
                feed_articles = await self._fetch_feed(feed_url, feed_name, max_per_feed, keywords)
                articles.extend(feed_articles)
            except Exception as e:
                errors += 1
                self.logger.error(f"Failed to fetch feed {feed_name}: {e}")
                continue

        self.logger.info(
            f"Scraped {len(articles)} articles from {len(feeds)} feeds "
            f"({errors} errors)"
        )

        return articles

    async def _fetch_feed(
        self,
        feed_url: str,
        feed_name: str,
        max_articles: int,
        keywords: List[str]
    ) -> List[ScrapedArticle]:
        """
        Fetch and parse a single RSS feed

        Args:
            feed_url: URL of the RSS feed
            feed_name: Display name of the feed
            max_articles: Maximum articles to return
            keywords: Keywords for filtering

        Returns:
            List of ScrapedArticle objects
        """
        self.logger.info(f"Fetching feed: {feed_name} ({feed_url})")

        feed = feedparser.parse(feed_url)

        if feed.bozo:
            self.logger.warning(f"Malformed RSS for {feed_name}: {feed.bozo_exception}")

        articles = []
        for entry in feed.entries[:max_articles]:
            article = self._parse_rss_entry(entry, feed_name)
            if article is None:
                continue

            # Keyword filtering
            if keywords and not self._matches_keywords(article, keywords):
                continue

            articles.append(article)

        return articles

    def _matches_keywords(self, article: ScrapedArticle, keywords: List[str]) -> bool:
        """
        Check if article matches any keyword

        Args:
            article: ScrapedArticle to check
            keywords: List of keywords

        Returns:
            True if matches any keyword or no keywords provided
        """
        if not keywords:
            return True

        text = f"{article.title} {article.content or ''}".lower()
        return any(kw.lower() in text for kw in keywords)

    def _get_default_feeds(self) -> List[Dict]:
        """
        Default AI blog feeds

        Returns:
            List of default feed configurations
        """
        return [
            {"name": "OpenAI", "url": "https://openai.com/blog/rss.xml"},
            {"name": "DeepMind", "url": "https://deepmind.google/blog/rss.xml"}
        ]
