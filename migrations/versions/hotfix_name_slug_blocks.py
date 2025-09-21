"""hotfix для добавления name и slug к blocks

Revision ID: hotfix_name_slug_blocks
Revises: add_name_slug_to_blocks
Create Date: 2025-09-15 18:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = 'hotfix_name_slug_blocks'
down_revision = 'add_name_slug_to_blocks'
branch_labels = None
depends_on = None


def upgrade():
    # Не используем инспектор схемы для проверки, просто пытаемся добавить столбцы
    # и игнорируем ошибки, если столбцы уже существуют
    try:
        op.execute(text("""
            ALTER TABLE brama.blocks ADD COLUMN IF NOT EXISTS name VARCHAR(50) NOT NULL DEFAULT 'legacy';
        """))
    except Exception as e:
        print(f"WARNING: Could not add name column to brama.blocks: {e}")
        # If there's a failure, try without DEFAULT
        try:
            op.execute(text("""
                ALTER TABLE brama.blocks ADD COLUMN IF NOT EXISTS name VARCHAR(50);
            """))
            # После добавления колонки без DEFAULT, обновляем все записи с NULL
            op.execute(text("""
                UPDATE brama.blocks SET name = 'legacy' WHERE name IS NULL;
            """))
            # Затем добавляем ограничение NOT NULL
            op.execute(text("""
                ALTER TABLE brama.blocks ALTER COLUMN name SET NOT NULL;
            """))
        except Exception as inner_e:
            print(f"ERROR: Failed to add name column even without DEFAULT: {inner_e}")

    try:
        op.execute(text("""
            ALTER TABLE brama.blocks ADD COLUMN IF NOT EXISTS slug VARCHAR(50);
        """))
    except Exception as e:
        print(f"WARNING: Could not add slug column to brama.blocks: {e}")


def downgrade():
    # We don't drop these columns in downgrade
    pass