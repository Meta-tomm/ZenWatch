"""add_user_article_scores_table

Revision ID: c2a82ac4fde2
Revises: 2d39bc6138ce
Create Date: 2026-01-06 16:36:30.189919

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'c2a82ac4fde2'
down_revision: Union[str, Sequence[str], None] = '2d39bc6138ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_article_scores table for personalized scoring."""
    op.create_table('user_article_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('article_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Float(), nullable=False, default=0.0),
        sa.Column('keyword_matches', sa.Integer(), default=0),
        sa.Column('scored_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'article_id', name='uix_user_article_score')
    )
    op.create_index('ix_user_article_scores_user_id', 'user_article_scores', ['user_id'])
    op.create_index('ix_user_article_scores_article_id', 'user_article_scores', ['article_id'])
    op.create_index('ix_user_article_scores_score', 'user_article_scores', ['score'])


def downgrade() -> None:
    """Drop user_article_scores table."""
    op.drop_index('ix_user_article_scores_score', table_name='user_article_scores')
    op.drop_index('ix_user_article_scores_article_id', table_name='user_article_scores')
    op.drop_index('ix_user_article_scores_user_id', table_name='user_article_scores')
    op.drop_table('user_article_scores')
