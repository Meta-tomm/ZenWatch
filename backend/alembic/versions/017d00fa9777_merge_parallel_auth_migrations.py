"""merge parallel auth migrations

Revision ID: 017d00fa9777
Revises: 6a2a33a30b04, a1b2c3d4e5f6
Create Date: 2026-01-06 10:05:06.888110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '017d00fa9777'
down_revision: Union[str, Sequence[str], None] = ('6a2a33a30b04', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
