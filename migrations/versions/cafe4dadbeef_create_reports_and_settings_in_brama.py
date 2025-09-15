"""create reports and settings in brama schema

Revision ID: cafe4dadbeef
Revises: b1a2c3d4e5f6
Create Date: 2025-09-15 00:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cafe4dadbeef'
down_revision = 'b1a2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE SCHEMA IF NOT EXISTS brama')
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('title', sa.String(length=128), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        schema='brama'
    )
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('facebook', sa.String(length=256), nullable=True),
        sa.Column('instagram', sa.String(length=256), nullable=True),
        sa.Column('telegram', sa.String(length=256), nullable=True),
        sa.Column('email', sa.String(length=256), nullable=True),
        schema='brama'
    )


def downgrade():
    op.drop_table('settings', schema='brama')
    op.drop_table('reports', schema='brama')
