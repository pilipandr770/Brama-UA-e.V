"""add name and slug to blocks table

Revision ID: add_name_slug_to_blocks
Revises: add_image_data_to_blocks
Create Date: 2025-09-15 17:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_name_slug_to_blocks'
down_revision = 'add_image_data_to_blocks'
branch_labels = None
depends_on = None


def upgrade():
    # Add name and slug columns to blocks table if they don't exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('blocks', schema='brama')]
    
    # Add name column if it doesn't exist
    if 'name' not in columns:
        op.add_column('blocks', 
                     sa.Column('name', sa.String(50), nullable=False, 
                               server_default='legacy'),
                     schema='brama')
    
    # Add slug column if it doesn't exist
    if 'slug' not in columns:
        op.add_column('blocks', 
                     sa.Column('slug', sa.String(50), nullable=True),
                     schema='brama')


def downgrade():
    # We don't drop these columns in downgrade as they might contain important data
    pass