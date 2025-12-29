"""add scraping_runs table

Revision ID: 8aff7deaacd5
Revises: bc8ef769a0c9
Create Date: 2025-12-29 19:14:36.518682

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8aff7deaacd5'
down_revision: Union[str, Sequence[str], None] = 'bc8ef769a0c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'scraping_runs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_id', sa.String(255), unique=True),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('started_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('articles_scraped', sa.Integer(), default=0),
        sa.Column('articles_saved', sa.Integer(), default=0),
        sa.Column('error_message', sa.Text(), nullable=True)
    )
    op.create_index('idx_scraping_runs_task_id', 'scraping_runs', ['task_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_scraping_runs_task_id')
    op.drop_table('scraping_runs')
