"""Create meeting tables

Revision ID: f3b4a8c729d5
Revises: fb534a67717f
Create Date: 2023-12-13 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f3b4a8c729d5'
down_revision = 'fb534a67717f'
branch_labels = None
depends_on = None

def upgrade():
    # Create enum types
    meeting_status = sa.Enum('planned', 'active', 'completed', 'cancelled', name='meetingstatus')
    vote_type = sa.Enum('yes', 'no', 'abstain', name='votetype')
    
    # Create meeting table
    op.create_table('meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=True),
        sa.Column('status', meeting_status, nullable=True),
        sa.Column('protocol_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create agenda items table
    op.create_table('agenda_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('requires_voting', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create meeting attendees table
    op.create_table('meeting_attendees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create meeting votes table
    op.create_table('meeting_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agenda_item_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('vote', vote_type, nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('voted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agenda_item_id'], ['agenda_items.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('messages')
    op.drop_table('meeting_votes')
    op.drop_table('meeting_attendees')
    op.drop_table('agenda_items')
    op.drop_table('meetings')
    op.execute('DROP TYPE meetingstatus')
    op.execute('DROP TYPE votetype')
