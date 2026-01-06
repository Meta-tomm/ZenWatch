from typing import List, Dict
from datetime import datetime
from bs4 import BeautifulSoup
from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.scrapers.strategies.rate_limit import RateLimiter
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="github",
    display_name="GitHub Trending",
    version="1.0.0"
)
class GitHubTrendingScraper(ScraperPlugin):
    """
    GitHub Trending scraper via HTML parsing

    Scrapes trending repositories from github.com/trending
    No API key required - uses public HTML page

    Features:
    - Scrapes daily/weekly/monthly trending repos
    - Filters by programming language
    - Filters by keywords in repo name/description
    - Returns validated Pydantic models
    """

    MAX_RETRIES = 3
    CACHE_TTL = 3600  # 1 hour
    TIMEOUT = 30.0

    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        self.rate_limiter = RateLimiter(requests_per_minute=30)
        self.base_url = "https://github.com/trending"

    def validate_config(self, config: Dict) -> bool:
        """No required config for GitHub Trending"""
        return True

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape trending repositories from GitHub

        Config options:
        - language: Filter by programming language (e.g., 'python', 'rust')
        - since: Time range ('daily', 'weekly', 'monthly')
        - max_articles: Maximum repos to return (default: 50)
        """
        language = config.get('language', '')
        since = config.get('since', 'daily')
        max_articles = config.get('max_articles', 50)

        self.logger.info(f"Fetching GitHub trending repos (language={language or 'all'}, since={since})")

        # Build URL
        url = self.base_url
        if language:
            url = f"{url}/{language}"

        params = {'since': since} if since else {}

        # Fetch HTML
        async with self.rate_limiter:
            response = await self._retry_request('GET', url, params=params)
            html = response.text

        # Parse HTML
        soup = BeautifulSoup(html, 'html.parser')
        repo_articles = soup.select('article.Box-row')

        articles = []
        for article in repo_articles:
            if len(articles) >= max_articles:
                break

            try:
                parsed = self._parse_repo(article, keywords)
                if parsed:
                    articles.append(parsed)
            except Exception as e:
                self.logger.warning(f"Failed to parse repo: {e}")
                continue

        self.logger.info(f"Scraped {len(articles)} trending repos from GitHub")
        return articles

    def _parse_repo(self, article, keywords: List[str]) -> ScrapedArticle | None:
        """Parse a single repo article element"""
        # Get repo name and URL
        h2 = article.select_one('h2 a')
        if not h2:
            return None

        repo_path = h2.get('href', '').strip('/')
        if not repo_path:
            return None

        repo_url = f"https://github.com/{repo_path}"
        repo_name = repo_path.replace('/', ' / ')

        # Get description
        desc_elem = article.select_one('p')
        description = desc_elem.get_text(strip=True) if desc_elem else ''

        # Filter by keywords
        text_to_search = f"{repo_name} {description}".lower()
        if keywords and not any(kw.lower() in text_to_search for kw in keywords):
            return None

        # Get language
        lang_elem = article.select_one('[itemprop="programmingLanguage"]')
        language = lang_elem.get_text(strip=True) if lang_elem else 'Unknown'

        # Get stars
        stars = 0
        stars_elem = article.select_one('a[href$="/stargazers"]')
        if stars_elem:
            stars_text = stars_elem.get_text(strip=True).replace(',', '')
            try:
                stars = int(stars_text)
            except ValueError:
                pass

        # Get today's stars
        today_stars = 0
        today_elem = article.select_one('span.d-inline-block.float-sm-right')
        if today_elem:
            today_text = today_elem.get_text(strip=True)
            try:
                today_stars = int(today_text.split()[0].replace(',', ''))
            except (ValueError, IndexError):
                pass

        # Get forks
        forks = 0
        forks_elem = article.select_one('a[href$="/forks"]')
        if forks_elem:
            forks_text = forks_elem.get_text(strip=True).replace(',', '')
            try:
                forks = int(forks_text)
            except ValueError:
                pass

        # Build tags
        tags = [language] if language != 'Unknown' else []
        if today_stars > 100:
            tags.append('hot')

        return ScrapedArticle(
            title=f"{repo_name} - {description[:100]}" if description else repo_name,
            url=repo_url,
            source_type='github',
            external_id=repo_path.replace('/', '_'),
            content=description,
            author=repo_path.split('/')[0] if '/' in repo_path else 'unknown',
            published_at=datetime.utcnow(),  # GitHub doesn't show creation date on trending
            tags=tags,
            upvotes=stars,
            comments_count=forks,  # Using forks as "engagement" metric
            raw_data={
                'language': language,
                'stars': stars,
                'forks': forks,
                'today_stars': today_stars
            }
        )
