"""create meetings tables in brama schema

Revision ID: dabbad00feed
Revises: cafe4dadbeef
Create Date: 2025-09-15 08:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'dabbad00feed'
down_revision = 'cafe4dadbeef'
branch_labels = None
depends_on = None


def upgrade():
    # Ensure schema exists
    op.execute('CREATE SCHEMA IF NOT EXISTS brama')
    
    # Get database connection to check table existence
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    conn = op.get_bind()
    
    # Create the enum types if they don't exist
    has_meeting_status_enum = False
    has_votetype_enum = False
    
    for enum_name in conn.dialect.get_enums():
        if enum_name['name'] == 'meetingstatus':
            has_meeting_status_enum = True
        elif enum_name['name'] == 'votetype':
            has_votetype_enum = True
    
    if not has_meeting_status_enum:
        meeting_status = postgresql.ENUM('planned', 'active', 'completed', 'cancelled',
                                         name='meetingstatus', create_type=False)
        meeting_status.create(bind=conn, checkfirst=True)
    
    if not has_votetype_enum:
        vote_type = postgresql.ENUM('yes', 'no', 'abstain',
                                    name='votetype', create_type=False)
        vote_type.create(bind=conn, checkfirst=True)

    # Create meetings table if it doesn't exist
    if not inspector.has_table('meetings', schema='brama'):
        op.create_table(
            'meetings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('date', sa.DateTime(), nullable=True),
            sa.Column('creator_id', sa.Integer(), nullable=True),
            sa.Column('status', sa.Enum('planned', 'active', 'completed', 'cancelled', 
                                        name='meetingstatus'), nullable=True),
            sa.Column('protocol_url', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.Column('reminder_sent', sa.Boolean(), nullable=True, default=False),
            sa.ForeignKeyConstraint(['creator_id'], ['brama.users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            schema='brama'
        )

    # Create agenda_items table if it doesn't exist
    if not inspector.has_table('agenda_items', schema='brama'):
        op.create_table(
            'agenda_items',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('meeting_id', sa.Integer(), nullable=True),
            sa.Column('title', sa.String(length=255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('order', sa.Integer(), nullable=True),
            sa.Column('requires_voting', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['meeting_id'], ['brama.meetings.id'], ),
            sa.PrimaryKeyConstraint('id'),
            schema='brama'
        )

    # Create meeting_attendees table if it doesn't exist
    if not inspector.has_table('meeting_attendees', schema='brama'):
        op.create_table(
            'meeting_attendees',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('meeting_id', sa.Integer(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('joined_at', sa.DateTime(), nullable=True),
            sa.Column('left_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['meeting_id'], ['brama.meetings.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['brama.users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            schema='brama'
        )

    # Create meeting_votes table if it doesn't exist
    if not inspector.has_table('meeting_votes', schema='brama'):
        op.create_table(
            'meeting_votes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('agenda_item_id', sa.Integer(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('vote', sa.Enum('yes', 'no', 'abstain', name='votetype'), nullable=True),
            sa.Column('comment', sa.Text(), nullable=True),
            sa.Column('voted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['agenda_item_id'], ['brama.agenda_items.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['brama.users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            schema='brama'
        )

    # Create messages table if it doesn't exist
    if not inspector.has_table('messages', schema='brama'):
        op.create_table(
            'messages',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('meeting_id', sa.Integer(), nullable=True),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['meeting_id'], ['brama.meetings.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['brama.users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            schema='brama'
        )

    # Create meeting_documents table if it doesn't exist
    if not inspector.has_table('meeting_documents', schema='brama'):
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
            sa.Column('uploaded_at', sa.DateTime(), nullable=True),
            sa.Column('is_public', sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(['meeting_id'], ['brama.meetings.id'], ),
            sa.ForeignKeyConstraint(['uploaded_by'], ['brama.users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            schema='brama'
        )


def downgrade():
    # Do not drop tables on downgrade for safety
    pass