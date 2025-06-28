import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database connection string from environment or config
DB_URI = os.getenv('DATABASE_URL')
DB_SCHEMA = os.getenv('DB_SCHEMA', 'brama')

if not DB_URI:
    print("ERROR: No database URI found in environment variables")
    sys.exit(1)

def fix_database():
    """Fix database issues with migrations and missing columns"""
    engine = create_engine(DB_URI)
    
    with engine.connect() as conn:
        # Check if translations column exists in blocks table
        check_query = f"""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_schema = '{DB_SCHEMA}' 
        AND table_name = 'blocks' 
        AND column_name = 'translations'
        """
        
        result = conn.execute(text(check_query)).fetchone()
        if not result:
            print("Adding missing 'translations' column to blocks table...")
            conn.execute(text(f"ALTER TABLE {DB_SCHEMA}.blocks ADD COLUMN translations TEXT"))
            conn.commit()
            print("Column added successfully")
        else:
            print("The 'translations' column already exists in the blocks table")
        
        # Check current version
        current = conn.execute(text(f"SELECT version_num FROM {DB_SCHEMA}.alembic_version")).fetchone()
        print(f"Current version: {current[0] if current else 'None'}")
        
        # Update to our latest version
        if current:
            conn.execute(text(f"DELETE FROM {DB_SCHEMA}.alembic_version"))
        
        # Insert our head revision
        conn.execute(text(f"INSERT INTO {DB_SCHEMA}.alembic_version VALUES ('fb534a67717f')"))
        conn.commit()
        
        # Verify the update
        new_version = conn.execute(text(f"SELECT version_num FROM {DB_SCHEMA}.alembic_version")).fetchone()
        print(f"Updated version: {new_version[0]}")
        
    print("Database fixes applied successfully!")

if __name__ == "__main__":
    fix_database()
