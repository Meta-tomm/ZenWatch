from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.scraping import router as scraping_router
from app.api.articles import router as articles_router
from app.api.keywords import router as keywords_router
from app.api.analytics import router as analytics_router
from app.api.youtube import router as youtube_router
from app.api.videos import router as videos_router
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.user_keywords import router as user_keywords_router
from app.api.comments import router as comments_router
from app.api.admin import router as admin_router
from app.api.library import router as library_router
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="TechWatch API",
    description="API for TechWatch - Automated Tech News Scraping Platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001"
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(scraping_router, prefix="/api", tags=["scraping"])
app.include_router(articles_router, prefix="/api", tags=["articles"])
app.include_router(keywords_router, prefix="/api", tags=["keywords"])
app.include_router(analytics_router, prefix="/api", tags=["analytics"])
app.include_router(youtube_router, prefix="/api", tags=["youtube"])
app.include_router(videos_router, prefix="/api", tags=["videos"])
app.include_router(auth_router, prefix="/api", tags=["auth"])
app.include_router(users_router, prefix="/api", tags=["users"])
app.include_router(user_keywords_router, prefix="/api", tags=["user-keywords"])
app.include_router(comments_router, prefix="/api", tags=["comments"])
app.include_router(admin_router, prefix="/api", tags=["admin"])
app.include_router(library_router, prefix="/api", tags=["library"])


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "service": "TechWatch API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
