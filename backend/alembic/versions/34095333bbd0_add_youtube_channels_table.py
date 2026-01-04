"""add youtube channels table

Revision ID: 34095333bbd0
Revises: d9e2f5a7b3c4
Create Date: 2026-01-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34095333bbd0'
down_revision: Union[str, Sequence[str], None] = 'd9e2f5a7b3c4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'youtube_channels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('channel_id', sa.String(255), nullable=False),
        sa.Column('channel_name', sa.String(255), nullable=False),
        sa.Column('channel_url', sa.Text(), nullable=False),
        sa.Column('rss_feed_url', sa.Text(), nullable=False),
        sa.Column('thumbnail_url', sa.Text(), nullable=True),
        sa.Column('subscriber_count', sa.Integer(), server_default='0'),
        sa.Column('is_active', sa.Boolean(), server_default='true'),
        sa.Column('is_suggested', sa.Boolean(), server_default='false'),
        sa.Column('suggestion_score', sa.Float(), nullable=True),
        sa.Column('suggestion_reason', sa.Text(), nullable=True),
        sa.Column('last_checked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index('idx_youtube_channels_active', 'youtube_channels', ['is_active'])
    op.create_index('idx_youtube_channels_suggested', 'youtube_channels', ['is_suggested', 'suggestion_score'])
    op.create_unique_constraint('uq_youtube_channel_id', 'youtube_channels', ['channel_id'])

def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_youtube_channels_suggested', 'youtube_channels')
    op.drop_index('idx_youtube_channels_active', 'youtube_channels')
    op.drop_table('youtube_channels')
