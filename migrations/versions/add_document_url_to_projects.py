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
    # Detect database dialect
    dialect = op.get_bind().dialect.name
    is_sqlite = dialect == 'sqlite'
    is_postgresql = dialect == 'postgresql'
    
    try:
        if is_sqlite:
            # SQLite doesn't support schema
            with op.batch_alter_table('projects') as batch_op:
                batch_op.add_column(sa.Column('document_url', sa.String(300), nullable=True))
                
                # Add image_data and image_mimetype columns if they don't exist
                try:
                    inspector = sa.inspect(op.get_bind())
                    columns = [c['name'] for c in inspector.get_columns('projects')]
                    
                    if 'image_data' not in columns:
                        batch_op.add_column(sa.Column('image_data', sa.LargeBinary(), nullable=True))
                        print("Added 'image_data' column to projects table")
                        
                    if 'image_mimetype' not in columns:
                        batch_op.add_column(sa.Column('image_mimetype', sa.String(64), nullable=True))
                        print("Added 'image_mimetype' column to projects table")
                except Exception as e:
                    print(f"Warning: Error checking/adding image columns: {e}")
                
                print("Added 'document_url' column to projects table")
        else:
            # PostgreSQL with schema
            op.add_column('projects', 
                        sa.Column('document_url', sa.String(300), nullable=True),
                        schema='brama')
                        
            # Add image_data and image_mimetype columns if they don't exist
            try:
                inspector = sa.inspect(op.get_bind())
                columns = [c['name'] for c in inspector.get_columns('projects', schema='brama')]
                
                if 'image_data' not in columns:
                    if is_postgresql:
                        from sqlalchemy.dialects.postgresql import BYTEA
                        op.add_column('projects', 
                                    sa.Column('image_data', BYTEA(), nullable=True),
                                    schema='brama')
                    else:
                        op.add_column('projects', 
                                    sa.Column('image_data', sa.LargeBinary(), nullable=True),
                                    schema='brama')
                    print("Added 'image_data' column to brama.projects table")
                    
                if 'image_mimetype' not in columns:
                    op.add_column('projects', 
                                sa.Column('image_mimetype', sa.String(64), nullable=True),
                                schema='brama')
                    print("Added 'image_mimetype' column to brama.projects table")
            except Exception as e:
                print(f"Warning: Error checking/adding image columns: {e}")
            
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