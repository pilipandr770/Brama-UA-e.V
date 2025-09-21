"""add document_url to projects table

Revision ID: add_document_url_to_projects
Revises: hotfix_name_slug_blocks
Create Date: 2025-09-21 19:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_document_url_to_projects'
down_revision = 'hotfix_name_slug_blocks'
branch_labels = None
depends_on = None


def upgrade():
    """Add document_url column to projects table, with support for SQLite"""
    # Detect if we're using SQLite
    is_sqlite = op.get_bind().dialect.name == 'sqlite'
    
    try:
        if is_sqlite:
            # SQLite doesn't support schema
            with op.batch_alter_table('projects') as batch_op:
                batch_op.add_column(sa.Column('document_url', sa.String(300), nullable=True))
                print("Added 'document_url' column to projects table")
        else:
            # PostgreSQL with schema
            op.add_column('projects', 
                        sa.Column('document_url', sa.String(300), nullable=True),
                        schema='brama')
            print("Added 'document_url' column to brama.projects table")
    except Exception as e:
        print(f"Warning: Error adding document_url column: {e}")


def downgrade():
    """Drop columns added in upgrade"""
    is_sqlite = op.get_bind().dialect.name == 'sqlite'
    
    try:
        if is_sqlite:
            with op.batch_alter_table('projects') as batch_op:
                batch_op.drop_column('document_url')
        else:
            op.drop_column('projects', 'document_url', schema='brama')
    except Exception as e:
        print(f"Warning: Error removing document_url column: {e}")