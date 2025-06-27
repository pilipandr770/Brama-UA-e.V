"""
This script applies the necessary database changes to fix the migration issues.
It creates the required tables, avoiding conflicts with existing ones, and fixes any case mismatches
between Python enums and database values.
"""

import os
import sys
from sqlalchemy import text
from app import db, create_app
from app.models.user import UserRole

app = create_app()

def fix_enum_case_postgres(conn):
    print("[INFO] Fixing userrole enum type in PostgreSQL to use lowercase values...")
    # 1. Change all roles to uppercase (so they match the current enum)
    conn.execute(text("UPDATE users SET role = UPPER(role);"))
    # 2. Rename the old enum type
    conn.execute(text("ALTER TYPE userrole RENAME TO userrole_old;"))
    # 3. Create the new enum type with lowercase values
    conn.execute(text("CREATE TYPE userrole AS ENUM ('member', 'admin', 'founder');"))
    # 4. Alter the column to use text temporarily
    conn.execute(text("ALTER TABLE users ALTER COLUMN role TYPE text;"))
    # 5. Convert all roles to lowercase (so they match the new enum)
    conn.execute(text("UPDATE users SET role = LOWER(role);"))
    # 6. Alter the column to use the new enum type
    conn.execute(text("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole;"))
    # 7. Drop the old enum type
    conn.execute(text("DROP TYPE userrole_old;"))
    print("[INFO] userrole enum type fixed!")

def fix_meetingstatus_enum_case_postgres(conn):
    print("[INFO] Fixing meetingstatus enum type in PostgreSQL to use lowercase values...")
    # 1. Change all statuses to uppercase (so they match the current enum)
    conn.execute(text("UPDATE meetings SET status = UPPER(status);"))
    # 2. Rename the old enum type
    conn.execute(text("ALTER TYPE meetingstatus RENAME TO meetingstatus_old;"))
    # 3. Create the new enum type with lowercase values
    conn.execute(text("CREATE TYPE meetingstatus AS ENUM ('planned', 'active', 'completed', 'cancelled');"))
    # 4. Alter the column to use text temporarily
    conn.execute(text("ALTER TABLE meetings ALTER COLUMN status TYPE text;"))
    # 5. Convert all statuses to lowercase (so they match the new enum)
    conn.execute(text("UPDATE meetings SET status = LOWER(status);"))
    # 6. Alter the column to use the new enum type
    conn.execute(text("ALTER TABLE meetings ALTER COLUMN status TYPE meetingstatus USING status::meetingstatus;"))
    # 7. Drop the old enum type
    conn.execute(text("DROP TYPE meetingstatus_old;"))
    print("[INFO] meetingstatus enum type fixed!")

def fix_migration():
    with app.app_context():
        try:
            # Execute SQL statements to create the necessary tables and types
            conn = db.engine.connect()
            
            # Handle the case mismatch issue by modifying our Python models to match the database
            # instead of trying to modify the database
            from app.models.user import UserRole
            from app.models.meeting import MeetingStatus, VoteType
            
            # Create enums if they don't exist - using lowercase to match existing database
            conn.execute(text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'votetype') THEN
                        CREATE TYPE votetype AS ENUM ('yes', 'no', 'abstain');
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'meetingstatus') THEN
                        CREATE TYPE meetingstatus AS ENUM ('planned', 'active', 'completed', 'cancelled');
                    END IF;
                    
                    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'userrole') THEN
                        CREATE TYPE userrole AS ENUM ('member', 'admin', 'founder');
                    END IF;
                END $$;
            """))
            
            # Add role column to users if it doesn't exist
            conn.execute(text("""
                DO $$ 
                BEGIN 
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'role') THEN
                        ALTER TABLE users ADD COLUMN role userrole DEFAULT 'MEMBER';
                    END IF;
                END $$;
            """))
            
            # Create meetings table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS meetings (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    date TIMESTAMP,
                    creator_id INTEGER REFERENCES users(id),
                    status meetingstatus DEFAULT 'PLANNED',
                    protocol_url VARCHAR(255),
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """))
            
            # Create agenda_items table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS agenda_items (
                    id SERIAL PRIMARY KEY,
                    meeting_id INTEGER REFERENCES meetings(id),
                    title VARCHAR(255) NOT NULL,
                    description TEXT,
                    "order" INTEGER DEFAULT 0,
                    requires_voting BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """))
            
            # Create meeting_attendees table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS meeting_attendees (
                    id SERIAL PRIMARY KEY,
                    meeting_id INTEGER REFERENCES meetings(id),
                    user_id INTEGER REFERENCES users(id),
                    joined_at TIMESTAMP DEFAULT NOW(),
                    left_at TIMESTAMP
                );
            """))
            
            # Create meeting_votes table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS meeting_votes (
                    id SERIAL PRIMARY KEY,
                    agenda_item_id INTEGER REFERENCES agenda_items(id),
                    user_id INTEGER REFERENCES users(id),
                    vote votetype,
                    comment TEXT,
                    voted_at TIMESTAMP DEFAULT NOW()
                );
            """))
            
            # Create messages table if it doesn't exist
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    meeting_id INTEGER REFERENCES meetings(id),
                    user_id INTEGER REFERENCES users(id),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """))
            
            # Set current admins as founders - using lowercase to match database
            conn.execute(text("""
                UPDATE users
                SET role = 'founder'
                WHERE is_admin = true;
            """))
            
            # Create alembic_version table if it doesn't exist and mark migration as complete
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS alembic_version (
                    version_num VARCHAR(32) PRIMARY KEY
                );
                
                INSERT INTO alembic_version (version_num)
                VALUES ('founder_meetings_addition')
                ON CONFLICT (version_num) DO NOTHING;
            """))
            
            conn.commit()
            conn.close()
            print("✅ Migration fixes applied successfully!")
        except Exception as e:
            print(f"❌ Error applying migration fixes: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(fix_migration())
