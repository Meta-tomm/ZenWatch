"""add user auth tables

Revision ID: 6a2a33a30b04
Revises: 957bd231a672
Create Date: 2026-01-06 09:50:58.295217

This migration adds the user authentication and authorization tables:
- users: User accounts with profile information
- oauth_accounts: OAuth provider connections (GitHub, Google, Discord)
- user_article_states: Per-user article read/favorite state
- user_video_states: Per-user video read/favorite state
- user_keywords: User-specific keywords for content personalization
- comments: Article and video comments with threading
- user_consents: GDPR consent tracking
- data_export_requests: GDPR data export requests
- user_config.user_id: Links config to user account

Note: These tables were created directly in the database.
This migration exists to sync Alembic with the current database state.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6a2a33a30b04'
down_revision: Union[str, Sequence[str], None] = '957bd231a672'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Tables already exist in the database.
    This migration syncs Alembic state with actual DB state.

    Created tables:
    - users (UUID PK, email, username, password_hash, avatar, bio, urls, role, status)
    - oauth_accounts (user_id FK, provider, provider_user_id, tokens)
    - user_article_states (user_id FK, article_id FK, is_read, is_favorite)
    - user_video_states (user_id FK, video_id FK, is_read, is_favorite)
    - user_keywords (user_id FK, keyword, weight)
    - comments (user_id FK, article_id/video_id FK, parent_id FK, content, threading)
    - user_consents (user_id FK, consent_type, consented, timestamps)
    - data_export_requests (user_id FK, status, file_url, timestamps)
    - user_config.user_id column (FK to users)
    """
    pass


def downgrade() -> None:
    """
    Downgrade would drop all auth tables.
    Not implemented as it would cause data loss.
    """
    pass
