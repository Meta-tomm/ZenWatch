from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.scraping import router as scraping_router
from app.api.articles import router as articles_router
from app.api.keywords import router as keywords_router
from app.api.analytics import router as analytics_router
from app.api.youtube import router as youtube_router
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
