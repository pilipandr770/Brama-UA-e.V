"""
Add meeting documents and reminder functionality
"""
import sqlalchemy as sa
from alembic import op
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'ac4cda9e7cef'
down_revision = '788419ababfb'  # ID предыдущей миграции
branch_labels = None
depends_on = None

def upgrade():
    # Create meeting_documents table
    op.create_table(
        'meeting_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_data', sa.LargeBinary(), nullable=False),
        sa.Column('file_mimetype', sa.String(length=128), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=True, default=datetime.utcnow),
        sa.Column('is_public', sa.Boolean(), nullable=True, default=False),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add reminder_sent column to meetings table
    op.add_column('meetings', sa.Column('reminder_sent', sa.Boolean(), nullable=True, default=False))


def downgrade():
    # Drop reminder_sent column from meetings table
    op.drop_column('meetings', 'reminder_sent')
    
    # Drop meeting_documents table
    op.drop_table('meeting_documents')
