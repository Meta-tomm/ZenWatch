"""add video fields to articles

Revision ID: 957bd231a672
Revises: 34095333bbd0
Create Date: 2026-01-03 21:13:29.345841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '957bd231a672'
down_revision: Union[str, Sequence[str], None] = '34095333bbd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('articles', sa.Column('video_id', sa.String(255), nullable=True))
    op.add_column('articles', sa.Column('thumbnail_url', sa.Text(), nullable=True))
    op.add_column('articles', sa.Column('duration_seconds', sa.Integer(), nullable=True))
    op.add_column('articles', sa.Column('view_count', sa.Integer(), nullable=True))
    op.add_column('articles', sa.Column('is_video', sa.Boolean(), default=False))

    op.create_index('idx_articles_video', 'articles', ['is_video'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_articles_video', 'articles')
    op.drop_column('articles', 'is_video')
    op.drop_column('articles', 'view_count')
    op.drop_column('articles', 'duration_seconds')
    op.drop_column('articles', 'thumbnail_url')
    op.drop_column('articles', 'video_id')
