# Schemas package
from app.schemas.article import (
    ArticleCreate,
    ArticleResponse,
    VideoResponse,
    PaginatedArticlesResponse,
    PaginatedVideosResponse,
)
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    AuthResponse,
    RefreshResponse,
    OAuthRedirectResponse,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserPublicProfile,
    UserExportData,
    AdminUserUpdate,
    PaginatedUsersResponse,
)
from app.schemas.user_keyword import (
    UserKeywordCreate,
    UserKeywordUpdate,
    UserKeywordResponse,
    UserKeywordList,
)
from app.schemas.comment import (
    CommentTargetType,
    CommentCreate,
    CommentUpdate,
    CommentResponse,
    CommentWithReplies,
    PaginatedCommentsResponse,
    AdminCommentResponse,
)

__all__ = [
    # Article
    "ArticleCreate",
    "ArticleResponse",
    "VideoResponse",
    "PaginatedArticlesResponse",
    "PaginatedVideosResponse",
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "AuthResponse",
    "RefreshResponse",
    "OAuthRedirectResponse",
    # User
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserPublicProfile",
    "UserExportData",
    "AdminUserUpdate",
    "PaginatedUsersResponse",
    # User Keyword
    "UserKeywordCreate",
    "UserKeywordUpdate",
    "UserKeywordResponse",
    "UserKeywordList",
    # Comment
    "CommentTargetType",
    "CommentCreate",
    "CommentUpdate",
    "CommentResponse",
    "CommentWithReplies",
    "PaginatedCommentsResponse",
    "AdminCommentResponse",
]
