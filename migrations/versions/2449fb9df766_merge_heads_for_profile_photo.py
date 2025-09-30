"""merge heads for profile photo

Revision ID: 2449fb9df766
Revises: 924f6a78e525, add_image_data_field, add_profile_photo_to_user
Create Date: 2025-06-27 12:44:53.448349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2449fb9df766'
down_revision = ('924f6a78e525', 'add_image_data_field', 'add_profile_photo_to_user')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
