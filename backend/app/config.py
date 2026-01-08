from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str = "postgresql://techwatch_user:techwatch_password@localhost:5432/techwatch"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # API Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    ENVIRONMENT: str = "development"

    # JWT Settings
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # OAuth Settings
    OAUTH_GITHUB_CLIENT_ID: Optional[str] = None
    OAUTH_GITHUB_CLIENT_SECRET: Optional[str] = None
    OAUTH_GOOGLE_CLIENT_ID: Optional[str] = None
    OAUTH_GOOGLE_CLIENT_SECRET: Optional[str] = None
    OAUTH_DISCORD_CLIENT_ID: Optional[str] = None
    OAUTH_DISCORD_CLIENT_SECRET: Optional[str] = None

    # Frontend URL for OAuth redirects
    FRONTEND_URL: str = "http://localhost:3000"

    # Anthropic API
    ANTHROPIC_API_KEY: Optional[str] = None

    # Reddit API
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    REDDIT_USER_AGENT: str = "TechWatch/1.0"

    # Dev.to API
    DEVTO_API_KEY: Optional[str] = None

    # YouTube API
    YOUTUBE_API_KEY: Optional[str] = None

    # Gemini API
    GEMINI_API_KEY: Optional[str] = None

    # Email SMTP
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@techwatch.local"

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Allow extra env vars without breaking


settings = Settings()
