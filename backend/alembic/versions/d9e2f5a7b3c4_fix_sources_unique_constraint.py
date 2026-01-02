"""fix_sources_unique_constraint

Revision ID: d9e2f5a7b3c4
Revises: 54deecb1beb5
Create Date: 2025-12-30 20:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9e2f5a7b3c4'
down_revision = '54deecb1beb5'
branch_labels = None
depends_on = None


def upgrade():
    # Drop unique constraint on type column
    with op.batch_alter_table('sources', schema=None) as batch_op:
        batch_op.drop_constraint('uq_sources_type', type_='unique')
        batch_op.create_unique_constraint('uq_sources_name', ['name'])


def downgrade():
    # Restore unique constraint on type column
    with op.batch_alter_table('sources', schema=None) as batch_op:
        batch_op.drop_constraint('uq_sources_name', type_='unique')
        batch_op.create_unique_constraint('uq_sources_type', ['type'])
