"""add block_id to project

Revision ID: add_block_id_to_project
Revises: 5607adf21cb6
Create Date: 2025-06-20

"""
from alembic import op
import sqlalchemy as sa

revision = 'add_block_id_to_project'
down_revision = '5607adf21cb6'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('projects', sa.Column('block_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_project_block', 'projects', 'blocks', ['block_id'], ['id'])

def downgrade():
    op.drop_constraint('fk_project_block', 'projects', type_='foreignkey')
    op.drop_column('projects', 'block_id')
