from app.schemas.article import (
    ArticleCreate,
    ArticleResponse,
    VideoResponse,
    PaginatedArticlesResponse,
    PaginatedVideosResponse,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPublicProfile,
    OAuthAccountResponse,
    UserWithOAuth,
)
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChangeRequest,
    EmailVerificationRequest,
    OAuthCallbackRequest,
    OAuthLinkRequest,
)
from app.schemas.comment import (
    CommentCreate,
    CommentUpdate,
    CommentAuthor,
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
    DataExportRequestResponse,
    DataDeletionRequest,
    UserDataExport,
)

__all__ = [
    # Article schemas
    "ArticleCreate",
    "ArticleResponse",
    "VideoResponse",
    "PaginatedArticlesResponse",
    "PaginatedVideosResponse",
    # User schemas
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserPublicProfile",
    "OAuthAccountResponse",
    "UserWithOAuth",
    # Auth schemas
    "LoginRequest",
    "RegisterRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "PasswordResetRequest",
    "PasswordResetConfirm",
    "PasswordChangeRequest",
    "EmailVerificationRequest",
    "OAuthCallbackRequest",
    "OAuthLinkRequest",
    # Comment schemas
    "CommentCreate",
    "CommentUpdate",
    "CommentAuthor",
    "CommentResponse",
    "CommentThread",
    "PaginatedCommentsResponse",
    # Consent schemas
    "ConsentCreate",
    "ConsentUpdate",
    "ConsentResponse",
    "ConsentStatusResponse",
    "DataExportRequestCreate",
    "DataExportRequestResponse",
    "DataDeletionRequest",
    "UserDataExport",
]
