from typing import List, Dict, Optional
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote

from app.scrapers.base import ScraperPlugin
from app.scrapers.registry import scraper_plugin
from app.scrapers.strategies.rate_limit import RateLimiter
from app.schemas.scraped_article import ScrapedArticle


@scraper_plugin(
    name="arxiv",
    display_name="arXiv",
    version="1.0.0"
)
class ArxivScraper(ScraperPlugin):
    """
    arXiv scraper using the arXiv API

    API docs: https://info.arxiv.org/help/api/index.html
    Rate limit: ~3 req/s (official recommendation)

    Features:
    - Searches in cs.AI, cs.CL, cs.LG, cs.MA categories
    - Filters by keywords in title/abstract
    - Parses Atom XML response
    - Returns validated Pydantic models
    """

    # Configuration
    MAX_RETRIES = 3
    CACHE_TTL = 3600  # 1 hour (research papers don't change often)
    TIMEOUT = 30.0

    # Arxiv categories for AI/ML research
    CATEGORIES = ["cs.AI", "cs.CL", "cs.LG", "cs.MA"]

    # XML namespaces
    ATOM_NS = {'atom': 'http://www.w3.org/2005/Atom'}
    ARXIV_NS = {'arxiv': 'http://arxiv.org/schemas/atom'}

    def __init__(self, redis_client=None):
        super().__init__(redis_client)
        self.rate_limiter = RateLimiter(requests_per_minute=30)
        self.base_url = "https://export.arxiv.org/api/query"

    def validate_config(self, config: Dict) -> bool:
        """No special config required for arXiv"""
        return True

    async def scrape(self, config: Dict, keywords: List[str]) -> List[ScrapedArticle]:
        """
        Scrape papers from arXiv

        Strategy:
        1. Build search query with categories and keywords
        2. Fetch XML response from arXiv API
        3. Parse entries and filter by keywords
        4. Return validated ScrapedArticle objects
        """
        max_articles = config.get('max_articles', 50)

        self.logger.info(f"Fetching arXiv papers for keywords: {keywords}")

        articles = []
        errors = 0

        # Build and execute search query
        try:
            xml_response = await self._fetch_papers(keywords, max_articles)
            root = ET.fromstring(xml_response)

            # Parse each entry
            for entry in root.findall('atom:entry', self.ATOM_NS):
                try:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                except Exception as e:
                    errors += 1
                    self.logger.warning(f"Failed to parse arXiv entry: {e}")
                    continue

        except Exception as e:
            self.logger.error(f"Failed to fetch arXiv papers: {e}")
            return []

        self.logger.info(
            f"Fetched {len(articles)} arXiv papers "
            f"({errors} errors skipped)"
        )

        return articles[:max_articles]

    async def _fetch_papers(self, keywords: List[str], max_results: int) -> str:
        """
        Fetch papers from arXiv API

        Query format:
        - Categories: (cat:cs.AI OR cat:cs.CL OR ...)
        - Keywords: AND (all:keyword1 OR all:keyword2 OR ...)
        """
        # Build category query
        cat_query = " OR ".join(f"cat:{cat}" for cat in self.CATEGORIES)

        # Build keyword query (search in all fields: title, abstract, authors)
        if keywords:
            kw_query = " OR ".join(f"all:{quote(kw)}" for kw in keywords)
            search_query = f"({cat_query}) AND ({kw_query})"
        else:
            search_query = f"({cat_query})"

        async with self.rate_limiter:
            params = {
                'search_query': search_query,
                'max_results': max_results,
                'sortBy': 'submittedDate',
                'sortOrder': 'descending'
            }

            response = await self._retry_request(
                'GET',
                self.base_url,
                params=params
            )

            return response.text

    def _parse_entry(self, entry: ET.Element) -> Optional[ScrapedArticle]:
        """
        Parse arXiv Atom entry to ScrapedArticle

        Returns None if required fields are missing
        """
        try:
            # Extract title (remove newlines and extra whitespace)
            title_elem = entry.find('atom:title', self.ATOM_NS)
            if title_elem is None or not title_elem.text:
                return None
            title = ' '.join(title_elem.text.split())

            # Extract ID (format: http://arxiv.org/abs/2401.00001v1)
            id_elem = entry.find('atom:id', self.ATOM_NS)
            if id_elem is None or not id_elem.text:
                return None
            arxiv_id = id_elem.text.split('/')[-1]  # Get "2401.00001v1"

            # Extract URL (link with rel="alternate")
            url = None
            for link in entry.findall('atom:link', self.ATOM_NS):
                if link.get('rel') == 'alternate':
                    url = link.get('href')
                    break
            if not url:
                url = id_elem.text

            # Extract abstract/summary
            summary_elem = entry.find('atom:summary', self.ATOM_NS)
            content = ' '.join(summary_elem.text.split()) if summary_elem is not None and summary_elem.text else None

            # Extract authors (join multiple authors)
            authors = []
            for author in entry.findall('atom:author', self.ATOM_NS):
                name_elem = author.find('atom:name', self.ATOM_NS)
                if name_elem is not None and name_elem.text:
                    authors.append(name_elem.text)
            author_str = ', '.join(authors) if authors else None

            # Extract published date
            published_elem = entry.find('atom:published', self.ATOM_NS)
            if published_elem is not None and published_elem.text:
                # Format: 2024-01-15T10:30:00Z
                published_at = datetime.fromisoformat(
                    published_elem.text.replace('Z', '+00:00')
                )
            else:
                published_at = datetime.now()

            # Extract primary category as tag
            tags = []
            primary_cat = entry.find('arxiv:primary_category', self.ARXIV_NS)
            if primary_cat is not None:
                tags.append(primary_cat.get('term', ''))

            # Create validated ScrapedArticle
            return ScrapedArticle(
                title=title,
                url=url,
                source_type='arxiv',
                external_id=arxiv_id,
                content=content,
                author=author_str,
                published_at=published_at,
                tags=tags,
                upvotes=0,  # arXiv doesn't have upvotes
                comments_count=0,
                raw_data={'arxiv_id': arxiv_id, 'authors': authors}
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse arXiv entry: {e}")
            return None
