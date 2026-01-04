from app.models.article import Article
from app.models.source import Source
from app.models.scraping_run import ScrapingRun
from app.models.keyword import Keyword
from app.models.article_keyword import ArticleKeyword
from app.models.trend import Trend
from app.models.user_config import UserConfig
from app.models.youtube_channel import YouTubeChannel

__all__ = [
    "Article",
    "Source",
    "ScrapingRun",
    "Keyword",
    "ArticleKeyword",
    "Trend",
    "UserConfig",
    "YouTubeChannel",
]
