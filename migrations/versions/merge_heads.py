"""Merge heads

Revision ID: merge_heads
Revises: add_block_id_to_project, create_brama_table
Create Date: 2025-06-21 18:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'merge_heads'
down_revision = ('add_block_id_to_project', 'create_brama_table')
branch_labels = None
depends_on = None


def upgrade():
    # This migration doesn't need to do anything as it's just merging branches
    pass


def downgrade():
    # This migration doesn't need to do anything as it's just merging branches
    pass
