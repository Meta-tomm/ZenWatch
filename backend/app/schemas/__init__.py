from app.schemas.article import (
    ArticleCreate,
    ArticleResponse,
    VideoResponse,
    PaginatedArticlesResponse,
    PaginatedVideosResponse,
)
from app.schemas.keyword import KeywordCreate, KeywordUpdate, KeywordResponse
from app.schemas.user_config import UserConfigCreate, UserConfigUpdate, UserConfigResponse
from app.schemas.analytics import (
    DailyStatsResponse,
    CategoryStatsResponse,
    TrendResponse,
    AnalyticsSummaryResponse,
)
from app.schemas.scraped_article import ScrapedArticle
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPublicProfile,
    UserKeywordCreate,
    UserKeywordResponse,
    UserKeywordsListResponse,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    TokenPayload,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    OAuthCallbackRequest,
    OAuthAccountResponse,
)
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentThread,
    PaginatedCommentsResponse,
)
from app.schemas.consent import (
    ConsentCreate,
    ConsentUpdate,
    ConsentResponse,
    ConsentStatusResponse,
    DataExportRequestCreate,
    DataExportResponse,
    DataExportListResponse,
    AccountDeletionRequest,
    AccountDeletionResponse,
)

__all__ = [
    # Article schemas
    "ArticleCreate",
    "ArticleResponse",
    "VideoResponse",
    "PaginatedArticlesResponse",
    "PaginatedVideosResponse",
    # Keyword schemas
    "KeywordCreate",
    "KeywordUpdate",
    "KeywordResponse",
    # User config schemas
    "UserConfigCreate",
    "UserConfigUpdate",
    "UserConfigResponse",
    # Analytics schemas
    "DailyStatsResponse",
    "CategoryStatsResponse",
    "TrendResponse",
    "AnalyticsSummaryResponse",
    # Scraped article
    "ScrapedArticle",
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserPublicProfile",
    "UserKeywordCreate",
    "UserKeywordResponse",
    "UserKeywordsListResponse",
    # Auth schemas
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "TokenPayload",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChangeRequest",
    "OAuthCallbackRequest",
    "OAuthAccountResponse",
    # Comment schemas
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "CommentThread",
    "PaginatedCommentsResponse",
    # Consent schemas
    "ConsentCreate",
    "ConsentUpdate",
    "ConsentResponse",
    "ConsentStatusResponse",
    "DataExportRequestCreate",
    "DataExportResponse",
    "DataExportListResponse",
    "AccountDeletionRequest",
    "AccountDeletionResponse",
]
