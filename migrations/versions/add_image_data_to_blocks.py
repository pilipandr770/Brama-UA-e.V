"""add image data to blocks table

Revision ID: add_image_data_to_blocks
Revises: dabbad00feed
Create Date: 2025-09-15 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_image_data_to_blocks'
down_revision = 'dabbad00feed'
branch_labels = None
depends_on = None


def upgrade():
    """Add image_data and image_mimetype columns to blocks table, with support for SQLite"""
    # Detect if we're using SQLite
    is_sqlite = op.get_bind().dialect.name == 'sqlite'
    
    try:
        if is_sqlite:
            # SQLite doesn't support schema
            with op.batch_alter_table('blocks') as batch_op:
                batch_op.add_column(sa.Column('image_data', sa.LargeBinary(), nullable=True))
                batch_op.add_column(sa.Column('image_mimetype', sa.String(64), nullable=True))
        else:
            # PostgreSQL with schema
            op.add_column('blocks', 
                        sa.Column('image_data', sa.LargeBinary(), nullable=True),
                        schema='brama')
            op.add_column('blocks', 
                        sa.Column('image_mimetype', sa.String(64), nullable=True),
                        schema='brama')
    except Exception as e:
        print(f"Warning: Error adding image columns: {e}")


def downgrade():
    """Drop columns added in upgrade"""
    is_sqlite = op.get_bind().dialect.name == 'sqlite'
    
    try:
        if is_sqlite:
            with op.batch_alter_table('blocks') as batch_op:
                batch_op.drop_column('image_data')
                batch_op.drop_column('image_mimetype')
        else:
            op.drop_column('blocks', 'image_data', schema='brama')
            op.drop_column('blocks', 'image_mimetype', schema='brama')
    except Exception as e:
        print(f"Warning: Error removing image columns: {e}")