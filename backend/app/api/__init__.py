# API routes package
from app.api.articles import router as articles_router
from app.api.videos import router as videos_router
from app.api.analytics import router as analytics_router
from app.api.scraping import router as scraping_router
from app.api.keywords import router as keywords_router
from app.api.youtube import router as youtube_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.user_keywords import router as user_keywords_router
from app.api.comments import router as comments_router
from app.api.admin import router as admin_router
from app.api.library import router as library_router

__all__ = [
    "articles_router",
    "videos_router",
    "analytics_router",
    "scraping_router",
    "keywords_router",
    "youtube_router",
    "auth_router",
    "users_router",
    "user_keywords_router",
    "comments_router",
    "admin_router",
    "library_router",
]
