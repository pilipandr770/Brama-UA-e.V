"""empty message

Revision ID: 48857144b2f0
Revises: add_document_url_to_projects, ac4cda9e7cef, b9b4a944b3d8
Create Date: 2025-09-22 11:02:26.094170

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '48857144b2f0'
down_revision = ('add_document_url_to_projects', 'ac4cda9e7cef', 'b9b4a944b3d8')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
