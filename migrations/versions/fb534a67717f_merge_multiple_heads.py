"""merge multiple heads

Revision ID: fb534a67717f
Revises: 69dfdee2bd31, add_translations_to_block
Create Date: 2025-06-28 11:06:00.970337

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb534a67717f'
down_revision = ('69dfdee2bd31', 'add_translations_to_block')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
