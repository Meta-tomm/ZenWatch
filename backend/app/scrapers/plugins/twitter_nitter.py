from typing import List, Dict
from datetime import datetime
import feedparser
import re
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="twitter",
    display_name="Twitter/X",
    version="1.0.0"
)
class TwitterNitterScraper(ScraperPlugin):
    """
    Twitter/X scraper via Nitter RSS feeds (free alternative)

    Uses Nitter instances which provide RSS feeds for Twitter content
    No API key required - uses public Nitter RSS

    Feed formats:
    - User timeline: https://{nitter_instance}/{username}/rss
    - User with replies: https://{nitter_instance}/{username}/with_replies/rss
    - Search: https://{nitter_instance}/search/rss?f=tweets&q={query}

    Features:
    - Scrapes tech influencers and accounts
    - Filters by keywords
    - Automatic Nitter instance failover
    - Returns validated Pydantic models
    """

    MAX_RETRIES = 3
    CACHE_TTL = 900  # 15 minutes (Twitter is fast-moving)
    TIMEOUT = 30.0

    # Public Nitter instances (will try in order)
    # Note: Nitter instances are notoriously unreliable - they go down frequently
    # Check https://github.com/zedeus/nitter/wiki/Instances for updated list
    NITTER_INSTANCES = [
        'nitter.cz',
        'nitter.privacydev.net',
        'nitter.poast.org',
        'nitter.1d4.us',
        'nitter.kavin.rocks',
    ]

    # Default tech accounts to follow
    DEFAULT_ACCOUNTS = [
        'github',
        'veraborhec',
        'ThePrimeagen',
        'kelaboratory',
        'levelsio',
        'swaborhec',
        'aiaborhec',
        'OpenAI',
        'AnthropicAI',
        'rustlang',
        'golang',
        'typescript',
        'nodejs',
        'reactjs',
        'vuejs',
        'docker',
        'kuaborhetes',
    ]

    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        self._working_instance = None

    def validate_config(self, config: Dict) -> bool:
        """No required config for Twitter/Nitter"""
        return True

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape tweets from Twitter via Nitter RSS

        Config options:
        - accounts: List of Twitter handles to scrape (default: tech accounts)
        - search_queries: List of search terms
        - max_articles: Maximum tweets to return (default: 50)
        - include_replies: Include replies (default: False)
        """
        accounts = config.get('accounts', self.DEFAULT_ACCOUNTS)
        search_queries = config.get('search_queries', [])
        max_articles = config.get('max_articles', 50)
        include_replies = config.get('include_replies', False)

        self.logger.info(f"Fetching tweets from {len(accounts)} accounts via Nitter")

        # Find working Nitter instance
        nitter_base = await self._find_working_instance()
        if not nitter_base:
            self.logger.error("No working Nitter instance found")
            return []

        articles = []
        seen_urls = set()

        # Scrape account feeds
        for account in accounts:
            if len(articles) >= max_articles:
                break

            suffix = '/with_replies/rss' if include_replies else '/rss'
            feed_url = f"https://{nitter_base}/{account}{suffix}"
            account_tweets = await self._scrape_feed(feed_url, keywords, account)

            for tweet in account_tweets:
                if tweet.url not in seen_urls:
                    seen_urls.add(tweet.url)
                    articles.append(tweet)

        # Scrape search queries
        for query in search_queries:
            if len(articles) >= max_articles:
                break

            encoded_query = query.replace(' ', '+')
            feed_url = f"https://{nitter_base}/search/rss?f=tweets&q={encoded_query}"
            search_tweets = await self._scrape_feed(feed_url, keywords, f"search:{query}")

            for tweet in search_tweets:
                if tweet.url not in seen_urls:
                    seen_urls.add(tweet.url)
                    articles.append(tweet)

        # Limit and sort by date
        articles = sorted(articles, key=lambda x: x.published_at, reverse=True)[:max_articles]

        self.logger.info(f"Scraped {len(articles)} tweets from Twitter/Nitter")
        return articles

    async def _find_working_instance(self) -> str | None:
        """Find a working Nitter instance"""
        # Return cached instance if we have one
        if self._working_instance:
            return self._working_instance

        for instance in self.NITTER_INSTANCES:
            try:
                # Test with a simple request
                test_url = f"https://{instance}/github/rss"
                response = await self._retry_request('GET', test_url)
                if response.status_code == 200:
                    self._working_instance = instance
                    self.logger.info(f"Using Nitter instance: {instance}")
                    return instance
            except Exception as e:
                self.logger.debug(f"Nitter instance {instance} failed: {e}")
                continue

        return None

    async def _scrape_feed(
        self,
        feed_url: str,
        keywords: List[str],
        source_tag: str
    ) -> List[ScrapedArticle]:
        """Scrape a single Nitter RSS feed"""
        try:
            response = await self._retry_request('GET', feed_url)
            feed = feedparser.parse(response.text)

            if feed.bozo:
                self.logger.warning(f"Malformed RSS feed: {feed_url}")
                return []

            articles = []
            for entry in feed.entries[:20]:  # Limit per feed
                try:
                    article = self._parse_entry(entry, keywords, source_tag)
                    if article:
                        articles.append(article)
                except Exception as e:
                    self.logger.warning(f"Failed to parse tweet: {e}")
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
        """Parse a single RSS entry (tweet)"""
        # Get tweet content
        content = entry.get('title', '') or entry.get('summary', '')
        if not content:
            return None

        # Strip HTML
        from bs4 import BeautifulSoup
        text_content = BeautifulSoup(content, 'html.parser').get_text()

        # Filter by keywords
        if keywords and not any(kw.lower() in text_content.lower() for kw in keywords):
            return None

        # Get URL - convert Nitter URL to Twitter URL
        nitter_url = entry.get('link', '')
        twitter_url = self._nitter_to_twitter_url(nitter_url)
        if not twitter_url:
            return None

        # Get author from URL or entry
        author = entry.get('author', '')
        if not author:
            # Extract from URL: /username/status/123
            match = re.search(r'/([^/]+)/status/', nitter_url)
            if match:
                author = match.group(1)

        # Get published date
        published = datetime.utcnow()
        if 'published_parsed' in entry and entry.published_parsed:
            try:
                published = datetime(*entry.published_parsed[:6])
            except Exception:
                pass

        # Extract hashtags as tags
        tags = [source_tag]
        hashtags = re.findall(r'#(\w+)', text_content)
        for ht in hashtags[:4]:
            if ht.lower() not in [t.lower() for t in tags]:
                tags.append(ht)

        # Extract tweet ID from URL
        tweet_id = ''
        match = re.search(r'/status/(\d+)', twitter_url)
        if match:
            tweet_id = match.group(1)

        # Truncate title for display
        title = text_content[:150]
        if len(text_content) > 150:
            title = title.rsplit(' ', 1)[0] + '...'

        return ScrapedArticle(
            title=f"@{author}: {title}",
            url=twitter_url,
            source_type='twitter',
            external_id=tweet_id or nitter_url,
            content=text_content,
            author=author or 'unknown',
            published_at=published,
            tags=tags[:5],
            upvotes=0,  # Not available via RSS
            comments_count=0,
            raw_data={
                'nitter_url': nitter_url,
                'source_account': source_tag
            }
        )

    def _nitter_to_twitter_url(self, nitter_url: str) -> str | None:
        """Convert Nitter URL to Twitter URL"""
        if not nitter_url:
            return None

        # Extract path from Nitter URL
        # https://nitter.instance.com/user/status/123 -> https://twitter.com/user/status/123
        for instance in self.NITTER_INSTANCES:
            if instance in nitter_url:
                path = nitter_url.split(instance)[-1]
                return f"https://twitter.com{path}"

        # Try generic extraction
        match = re.search(r'/([^/]+/status/\d+)', nitter_url)
        if match:
            return f"https://twitter.com/{match.group(1)}"

        return nitter_url
