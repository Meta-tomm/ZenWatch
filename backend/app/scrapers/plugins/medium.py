from typing import List, Dict
from datetime import datetime
import feedparser
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="medium",
    display_name="Medium",
    version="1.0.0"
)
class MediumScraper(ScraperPlugin):
    """
    Medium scraper via RSS feeds

    Scrapes articles from Medium tags/publications via RSS
    No API key required - uses public RSS feeds

    RSS Feed formats:
    - Tag feed: https://medium.com/feed/tag/{tag}
    - Publication: https://medium.com/feed/{publication}
    - User: https://medium.com/feed/@{username}

    Features:
    - Scrapes multiple tags/publications
    - Filters by keywords in title/content
    - Returns validated Pydantic models
    """

    MAX_RETRIES = 3
    CACHE_TTL = 1800  # 30 minutes
    TIMEOUT = 30.0

    # Default tech tags to follow
    DEFAULT_TAGS = [
        'programming',
        'software-engineering',
        'artificial-intelligence',
        'machine-learning',
        'python',
        'javascript',
        'rust',
        'devops',
        'kubernetes',
        'web-development'
    ]

    def __init__(self, redis_client=None):
        super().__init__(redis_client)

    def validate_config(self, config: Dict) -> bool:
        """No required config for Medium"""
        return True

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape articles from Medium RSS feeds

        Config options:
        - tags: List of Medium tags to scrape (default: tech tags)
        - publications: List of publications to scrape
        - users: List of user handles to scrape
        - max_articles: Maximum articles to return (default: 50)
        """
        tags = config.get('tags', self.DEFAULT_TAGS)
        publications = config.get('publications', [])
        users = config.get('users', [])
        max_articles = config.get('max_articles', 50)

        self.logger.info(f"Fetching Medium articles from {len(tags)} tags, {len(publications)} publications")

        articles = []
        seen_urls = set()

        # Scrape tag feeds
        for tag in tags:
            if len(articles) >= max_articles:
                break
            feed_url = f"https://medium.com/feed/tag/{tag}"
            tag_articles = await self._scrape_feed(feed_url, keywords, tag)
            for article in tag_articles:
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    articles.append(article)

        # Scrape publication feeds
        for pub in publications:
            if len(articles) >= max_articles:
                break
            feed_url = f"https://medium.com/feed/{pub}"
            pub_articles = await self._scrape_feed(feed_url, keywords, pub)
            for article in pub_articles:
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    articles.append(article)

        # Scrape user feeds
        for user in users:
            if len(articles) >= max_articles:
                break
            feed_url = f"https://medium.com/feed/@{user}"
            user_articles = await self._scrape_feed(feed_url, keywords, f"@{user}")
            for article in user_articles:
                if article.url not in seen_urls:
                    seen_urls.add(article.url)
                    articles.append(article)

        # Limit to max_articles
        articles = articles[:max_articles]

        self.logger.info(f"Scraped {len(articles)} articles from Medium")
        return articles

    async def _scrape_feed(
        self,
        feed_url: str,
        keywords: List[str],
        source_tag: str
    ) -> List[ScrapedArticle]:
        """Scrape a single RSS feed"""
        try:
            # Fetch feed
            response = await self._retry_request('GET', feed_url)
            feed = feedparser.parse(response.text)

            if feed.bozo:
                self.logger.warning(f"Malformed RSS feed: {feed_url}")
                return []

            articles = []
            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry, keywords, source_tag)
                    if article:
                        articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Failed to parse entry: {e}")
                    continue

            return articles

        except Exception as e:
            self.logger.warning(f"Failed to fetch feed {feed_url}: {e}")
            return []

    def _parse_entry(
        self,
        entry,
        keywords: List[str],
        source_tag: str
    ) -> ScrapedArticle | None:
        """Parse a single RSS entry"""
        title = entry.get('title', '')
        if not title:
            return None

        # Get content/summary
        content = ''
        if 'content' in entry and entry.content:
            content = entry.content[0].get('value', '')
        elif 'summary' in entry:
            content = entry.summary

        # Strip HTML from content for keyword matching
        from bs4 import BeautifulSoup
        text_content = BeautifulSoup(content, 'html.parser').get_text()

        # Filter by keywords
        text_to_search = f"{title} {text_content}".lower()
        if keywords and not any(kw.lower() in text_to_search for kw in keywords):
            return None

        # Get URL
        url = entry.get('link', '')
        if not url:
            return None

        # Clean Medium URL (remove query params)
        if '?' in url:
            url = url.split('?')[0]

        # Get author
        author = entry.get('author', '')
        if not author and 'authors' in entry and entry.authors:
            author = entry.authors[0].get('name', 'unknown')

        # Get published date
        published = datetime.utcnow()
        if 'published_parsed' in entry and entry.published_parsed:
            try:
                published = datetime(*entry.published_parsed[:6])
            except Exception:
                pass

        # Extract tags from categories
        tags = [source_tag]
        if 'tags' in entry:
            for tag in entry.tags[:5]:
                term = tag.get('term', '')
                if term and term not in tags:
                    tags.append(term)

        # Estimate read time (assuming 200 words per minute)
        word_count = len(text_content.split())
        read_time = max(1, word_count // 200)

        return ScrapedArticle(
            title=title,
            url=url,
            source_type='medium',
            external_id=url.split('/')[-1].split('-')[-1] if url else '',
            content=text_content[:5000],  # Limit content length
            author=author or 'unknown',
            published_at=published,
            tags=tags[:5],
            upvotes=0,  # Medium doesn't expose claps via RSS
            comments_count=0,
            raw_data={
                'read_time_minutes': read_time,
                'source_tag': source_tag
            }
        )
