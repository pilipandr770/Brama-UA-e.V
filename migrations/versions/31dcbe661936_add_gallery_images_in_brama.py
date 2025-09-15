"""
Add gallery_images table in brama schema
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '31dcbe661936'
down_revision = '31dcbe661935'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'gallery_images',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('image_url', sa.String(length=300), nullable=True),
        sa.Column('image_data', sa.LargeBinary(), nullable=True),
        sa.Column('image_mimetype', sa.String(length=64), nullable=True),
        sa.Column('description', sa.String(length=256), nullable=True),
        sa.Column('block_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['block_id'], ['brama.blocks.id']),
        schema='brama'
    )


def downgrade():
    op.drop_table('gallery_images', schema='brama')
