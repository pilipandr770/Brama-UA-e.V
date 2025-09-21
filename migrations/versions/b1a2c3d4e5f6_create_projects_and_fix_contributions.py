"""create projects in brama schema and fix contributions type

Revision ID: b1a2c3d4e5f6
Revises: 31dcbe661936
Create Date: 2025-09-15 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'b1a2c3d4e5f6'
down_revision = '31dcbe661936'
branch_labels = None
depends_on = None


def upgrade():
    # Ensure schema exists (no-op if already present)
    op.execute('CREATE SCHEMA IF NOT EXISTS brama')

    # Create projects table in brama schema if it doesn't exist
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('problem_description', sa.Text(), nullable=False),
        sa.Column('goal', sa.Text(), nullable=False),
        sa.Column('target_audience', sa.Text(), nullable=False),
        sa.Column('implementation_plan', sa.Text(), nullable=False),
        sa.Column('executor_info', sa.Text(), nullable=False),
        sa.Column('total_budget', sa.Float(), nullable=False),
        sa.Column('budget_breakdown', sa.Text(), nullable=False),
        sa.Column('expected_result', sa.Text(), nullable=False),
        sa.Column('risks', sa.Text(), nullable=False),
        sa.Column('duration', sa.String(length=100), nullable=False),
        sa.Column('reporting_plan', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=True),
        sa.Column('location', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('social_links', sa.Text(), nullable=True),
        sa.Column('image_url', sa.String(length=300), nullable=True),
        sa.Column('image_data', sa.LargeBinary(), nullable=True),
        sa.Column('image_mimetype', sa.String(length=64), nullable=True),
        sa.Column('document_url', sa.String(length=300), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True, server_default='pending'),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('brama.users.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('block_id', sa.Integer(), sa.ForeignKey('brama.blocks.id'), nullable=True),
        schema='brama'
    )

    # Create votes table in brama schema if it doesn't exist
    op.create_table(
        'votes',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('brama.users.id'), nullable=False),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('brama.projects.id'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        schema='brama'
    )

    # Fix contributions type to FLOAT on Postgres (from TEXT)
    # Try a safe conversion: invalid values become 0
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_schema = 'brama' AND table_name = 'users' AND column_name = 'contributions' AND data_type <> 'double precision'
            ) THEN
                -- Create a temp column with float type
                ALTER TABLE brama.users ADD COLUMN contributions_tmp double precision;
                -- Copy data with safe cast
                UPDATE brama.users 
                SET contributions_tmp = CASE 
                    WHEN contributions ~ '^[0-9]+(\.[0-9]+)?$' THEN contributions::double precision 
                    ELSE 0
                END;
                -- Drop old column and rename
                ALTER TABLE brama.users DROP COLUMN contributions;
                ALTER TABLE brama.users RENAME COLUMN contributions_tmp TO contributions;
            END IF;
        END$$;
    """)


def downgrade():
    # Drop votes and projects tables (if needed)
    op.drop_table('votes', schema='brama')
    op.drop_table('projects', schema='brama')

    # Revert contributions to TEXT
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_schema = 'brama' AND table_name = 'users' AND column_name = 'contributions' AND data_type = 'double precision'
            ) THEN
                ALTER TABLE brama.users ADD COLUMN contributions_tmp text;
                UPDATE brama.users SET contributions_tmp = contributions::text;
                ALTER TABLE brama.users DROP COLUMN contributions;
                ALTER TABLE brama.users RENAME COLUMN contributions_tmp TO contributions;
            END IF;
        END$$;
    """)
