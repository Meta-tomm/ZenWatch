"""add_library_triage_fields

Revision ID: 76bdfd8b571f
Revises: 017d00fa9777
Create Date: 2026-01-06 15:45:07.959838

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76bdfd8b571f'
down_revision: Union[str, Sequence[str], None] = '017d00fa9777'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add library and triage fields to articles table."""
    op.add_column('articles', sa.Column('is_bookmarked', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('articles', sa.Column('is_dismissed', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('articles', sa.Column('bookmarked_at', sa.DateTime(), nullable=True))

    # Index for library queries (bookmarked items sorted by date)
    op.create_index('idx_articles_bookmarked', 'articles', ['is_bookmarked', 'bookmarked_at'])
    # Index for triage queries (exclude bookmarked/dismissed)
    op.create_index('idx_articles_triage', 'articles', ['is_bookmarked', 'is_dismissed', 'is_archived'])


def downgrade() -> None:
    """Remove library and triage fields from articles table."""
    op.drop_index('idx_articles_triage', table_name='articles')
    op.drop_index('idx_articles_bookmarked', table_name='articles')
    op.drop_column('articles', 'bookmarked_at')
    op.drop_column('articles', 'is_dismissed')
    op.drop_column('articles', 'is_bookmarked')
