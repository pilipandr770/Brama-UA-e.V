"""Add translations column to Block model

Revision ID: add_translations_to_block
Revises: c5067de689d1
Create Date: 2025-06-28 12:15:13.638264

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_translations_to_block'
down_revision = 'c5067de689d1'
branch_labels = None
depends_on = None


def upgrade():
    # Add translations column to blocks table
    op.add_column('blocks', sa.Column('translations', sa.Text(), nullable=True))


def downgrade():
    # Remove translations column from blocks table
    op.drop_column('blocks', 'translations')
