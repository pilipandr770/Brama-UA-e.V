"""initial_migration

Revision ID: 0
Revises: None
Create Date: 2025-06-21 17:47:49.859920

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Створення таблиці users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=256), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False, default=False),
        sa.Column('name', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('organization', sa.String(length=100), nullable=True),
        sa.Column('position', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    
    # Створення таблиці blocks
    op.create_table(
        'blocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('image_url', sa.String(length=300), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Створення таблиці gallery_images
    op.create_table(
        'gallery_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=128), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image', sa.LargeBinary(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Створення таблиці projects
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('block_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('image', sa.LargeBinary(), nullable=True),
        sa.ForeignKeyConstraint(['block_id'], ['blocks.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Створення таблиці settings
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=64), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )
    
    # Створення таблиці звітів
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=100), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Створення таблиці для голосування
    op.create_table(
        'votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'project_id')
    )


def downgrade():
    op.drop_table('votes')
    op.drop_table('reports')
    op.drop_table('settings')
    op.drop_table('projects')
    op.drop_table('gallery_images')
    op.drop_table('blocks')
    op.drop_table('users')
