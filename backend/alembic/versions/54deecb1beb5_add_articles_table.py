"""add articles table

Revision ID: 54deecb1beb5
Revises: 8aff7deaacd5
Create Date: 2025-12-30 19:33:37.360699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '54deecb1beb5'
down_revision: Union[str, Sequence[str], None] = '8aff7deaacd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'articles',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('source_id', sa.Integer(), nullable=True),
        sa.Column('external_id', sa.String(255), nullable=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('url', sa.Text(), nullable=False, unique=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('author', sa.String(255), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=False),
        sa.Column('scraped_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('category', sa.String(100), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('language', sa.String(10), default='en'),
        sa.Column('read_time_minutes', sa.Integer(), nullable=True),
        sa.Column('upvotes', sa.Integer(), default=0),
        sa.Column('comments_count', sa.Integer(), default=0),
        sa.Column('is_read', sa.Boolean(), default=False),
        sa.Column('is_favorite', sa.Boolean(), default=False),
        sa.Column('is_archived', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    op.create_index('idx_articles_url', 'articles', ['url'])
    op.create_index('idx_articles_score', 'articles', ['score'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_articles_score')
    op.drop_index('idx_articles_url')
    op.drop_table('articles')
