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
    """
    Улучшенная версия миграции для добавления отсутствующих колонок в таблицу blocks.
    Работает как с SQLite, так и с PostgreSQL, с учетом различной синтаксической поддержки.
    """
    # Определяем список схем для проверки
    schemas_to_check = ['brama', None]  # None = без схемы (как в SQLite)
    dialect = op.get_bind().dialect.name
    
    for schema in schemas_to_check:
        try:
            # Try to get columns for this schema
            inspector = sa.inspect(op.get_bind())
            table_name = 'blocks'
            try:
                columns = [c['name'] for c in inspector.get_columns(table_name, schema=schema)]
                # Successfully found the table with this schema
                schema_name = schema
                break
            except Exception:
                # This schema/table combination doesn't exist, try the next one
                continue
        except Exception:
            # If any error occurs, just continue to the next schema
            continue
    else:
        # If we get here, we couldn't find the table in any schema
        print("WARNING: Could not find 'blocks' table in any schema")
        return

    # Различные подходы в зависимости от диалекта базы данных
    if dialect == 'sqlite':
        # For SQLite, use batch_alter_table
        with op.batch_alter_table(table_name, schema=schema_name) as batch_op:
            # Add all potentially missing columns
            if 'name' not in columns:
                batch_op.add_column(sa.Column('name', sa.String(50), nullable=True))
                print(f"Added 'name' column to {table_name}")
            
            if 'slug' not in columns:
                batch_op.add_column(sa.Column('slug', sa.String(50), nullable=True))
                print(f"Added 'slug' column to {table_name}")
                
            if 'image_data' not in columns:
                batch_op.add_column(sa.Column('image_data', sa.LargeBinary, nullable=True))
                print(f"Added 'image_data' column to {table_name}")
                
            if 'image_mimetype' not in columns:
                batch_op.add_column(sa.Column('image_mimetype', sa.String(64), nullable=True))
                print(f"Added 'image_mimetype' column to {table_name}")
    else:
        # For PostgreSQL and others that support ADD COLUMN IF NOT EXISTS
        try:
            table_ref = f"{schema_name}.{table_name}" if schema_name else table_name
            
            # Add all potentially missing columns
            if 'name' not in columns:
                op.execute(text(f"ALTER TABLE {table_ref} ADD COLUMN IF NOT EXISTS name VARCHAR(50)"))
                print(f"Added 'name' column to {table_ref}")
            
            if 'slug' not in columns:
                op.execute(text(f"ALTER TABLE {table_ref} ADD COLUMN IF NOT EXISTS slug VARCHAR(50)"))
                print(f"Added 'slug' column to {table_ref}")
                
            if 'image_data' not in columns:
                op.execute(text(f"ALTER TABLE {table_ref} ADD COLUMN IF NOT EXISTS image_data BYTEA"))
                print(f"Added 'image_data' column to {table_ref}")
                
            if 'image_mimetype' not in columns:
                op.execute(text(f"ALTER TABLE {table_ref} ADD COLUMN IF NOT EXISTS image_mimetype VARCHAR(64)"))
                print(f"Added 'image_mimetype' column to {table_ref}")
        except Exception as e:
            print(f"ERROR: Failed to add columns using SQL: {e}")
            # Fallback to using batch_alter_table
            with op.batch_alter_table(table_name, schema=schema_name) as batch_op:
                if 'name' not in columns:
                    batch_op.add_column(sa.Column('name', sa.String(50), nullable=True))
                if 'slug' not in columns:
                    batch_op.add_column(sa.Column('slug', sa.String(50), nullable=True))
                if 'image_data' not in columns:
                    batch_op.add_column(sa.Column('image_data', sa.LargeBinary, nullable=True))
                if 'image_mimetype' not in columns:
                    batch_op.add_column(sa.Column('image_mimetype', sa.String(64), nullable=True))
    
    # Update values in the new columns
    try:
        table_ref = f"{schema_name}.{table_name}" if schema_name else table_name
        op.execute(text(f"UPDATE {table_ref} SET name = 'legacy' WHERE name IS NULL"))
        
        # Generate slugs based on ID for records with NULL slug
        op.execute(text(f"UPDATE {table_ref} SET slug = 'block_' || id WHERE slug IS NULL"))
        print(f"Updated default values in {table_ref}")
    except Exception as e:
        print(f"WARNING: Could not update values: {e}")


def downgrade():
    # We don't drop these columns in downgrade
    pass