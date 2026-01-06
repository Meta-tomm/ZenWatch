"""fix_youtube_is_video_flag

Revision ID: 2d39bc6138ce
Revises: 76bdfd8b571f
Create Date: 2026-01-06 16:17:23.738182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d39bc6138ce'
down_revision: Union[str, Sequence[str], None] = '76bdfd8b571f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Update existing YouTube articles to have is_video=True"""
    # Update articles from YouTube sources to have is_video=True
    op.execute("""
        UPDATE articles
        SET is_video = true
        WHERE source_id IN (
            SELECT id FROM sources WHERE type IN ('youtube_rss', 'youtube_trending', 'youtube')
        )
        AND is_video = false
    """)


def downgrade() -> None:
    """Revert is_video flag (no-op since we can't know original state)"""
    pass
