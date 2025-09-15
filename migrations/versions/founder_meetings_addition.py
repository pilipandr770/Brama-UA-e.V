"""Founder role and meetings models

Revision ID: founder_meetings_addition
Revises: d3555f676b02
Create Date: 2025-06-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import enum

# revision identifiers, used by Alembic.
revision = 'founder_meetings_addition'
down_revision = 'd3555f676b02'
branch_labels = None
depends_on = None

# Create the enum types in Python that match our SQLAlchemy models
class UserRole(enum.Enum):
    MEMBER = "member"
    ADMIN = "admin"
    FOUNDER = "founder"

class MeetingStatus(enum.Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class VoteType(enum.Enum):
    YES = "yes"
    NO = "no"
    ABSTAIN = "abstain"


def upgrade():
    # Create enum types in PostgreSQL
    user_role = postgresql.ENUM('member', 'admin', 'founder', name='userrole')
    meeting_status = postgresql.ENUM('planned', 'active', 'completed', 'cancelled', name='meetingstatus')
    vote_type = postgresql.ENUM('yes', 'no', 'abstain', name='votetype')
    
    user_role.create(op.get_bind())
    meeting_status.create(op.get_bind())
    vote_type.create(op.get_bind())

    # Add role column to users table
    op.add_column('users', sa.Column('role', sa.Enum(UserRole), server_default='member'))
    
    # Create meetings table
    op.create_table(
        'meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('creator_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum(MeetingStatus), default='planned'),
        sa.Column('protocol_url', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create agenda_items table
    op.create_table(
        'agenda_items',
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
    
    # Create meeting_attendees table
    op.create_table(
        'meeting_attendees',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create meeting_votes table
    op.create_table(
        'meeting_votes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agenda_item_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('vote', sa.Enum(VoteType), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('voted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['agenda_item_id'], ['agenda_items.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('meeting_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['meeting_id'], ['meetings.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Set current admins as founders too
    op.execute("""
    UPDATE users
    SET role = 'founder'
    WHERE is_admin = true
    """)


def downgrade():
    # Drop the tables
    op.drop_table('messages')
    op.drop_table('meeting_votes')
    op.drop_table('meeting_attendees')
    op.drop_table('agenda_items')
    op.drop_table('meetings')
    
    # Drop the role column from users
    op.drop_column('users', 'role')
    
    # Drop the enum types
    op.execute('DROP TYPE votetype')
    op.execute('DROP TYPE meetingstatus')
    op.execute('DROP TYPE userrole')
