"""Fix for meetings table creation

This script directly applies the SQL commands to create the meetings tables in the brama schema.
It fixes the issue with the original migration that tried to use conn.dialect.get_enums() which doesn't exist.

Usage:
    python fix_meetings_tables.py

"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def main():
    # Get the database URL from the environment variable or use the one from alembic.ini
    db_url = os.environ.get('DATABASE_URL', 'postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a.frankfurt-postgres.render.com/ittoken_db')
    
    # Replace 'postgres://' with 'postgresql://' if needed
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    # Parse the database URL to get connection parameters
    db_url = db_url.replace('postgresql://', '')
    user_pass, host_dbname = db_url.split('@')
    user, password = user_pass.split(':')
    host_port, dbname = host_dbname.split('/')
    
    if ':' in host_port:
        host, port = host_port.split(':')
    else:
        host = host_port
        port = 5432
    
    print(f"Connecting to PostgreSQL database: {host}:{port}/{dbname}")
    
    # Connect to the database
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Ensure the brama schema exists
        cursor.execute('CREATE SCHEMA IF NOT EXISTS brama')
        print("Schema 'brama' created if it didn't exist.")
        
        # Create the enum types if they don't exist
        create_enum_statements = [
            "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type JOIN pg_namespace ON pg_type.typnamespace = pg_namespace.oid WHERE pg_type.typname = 'meetingstatus' AND pg_namespace.nspname = 'brama') THEN CREATE TYPE brama.meetingstatus AS ENUM ('planned', 'active', 'completed', 'cancelled'); END IF; END $$;",
            "DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type JOIN pg_namespace ON pg_type.typnamespace = pg_namespace.oid WHERE pg_type.typname = 'votetype' AND pg_namespace.nspname = 'brama') THEN CREATE TYPE brama.votetype AS ENUM ('yes', 'no', 'abstain'); END IF; END $$;"
        ]
        
        for statement in create_enum_statements:
            cursor.execute(statement)
        print("Enum types created if they didn't exist.")
        
        # Check if meetings table exists
        cursor.execute("SELECT EXISTS(SELECT FROM pg_tables WHERE schemaname = 'brama' AND tablename = 'meetings')")
        meetings_exists = cursor.fetchone()[0]
        
        # Only create tables if they don't exist
        if not meetings_exists:
            # Create the meetings table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS brama.meetings (
                id SERIAL PRIMARY KEY,
                title VARCHAR(255) NOT NULL,
                description TEXT,
                date TIMESTAMP,
                creator_id INTEGER REFERENCES brama.users(id),
                status brama.meetingstatus,
                protocol_url VARCHAR(255),
                created_at TIMESTAMP,
                updated_at TIMESTAMP,
                reminder_sent BOOLEAN DEFAULT FALSE
            )
            """)
            print("Table 'meetings' created.")
            
            # Create agenda_items table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS brama.agenda_items (
                id SERIAL PRIMARY KEY,
                meeting_id INTEGER REFERENCES brama.meetings(id),
                title VARCHAR(255) NOT NULL,
                description TEXT,
                "order" INTEGER,
                requires_voting BOOLEAN,
                created_at TIMESTAMP
            )
            """)
            print("Table 'agenda_items' created.")
            
            # Create meeting_attendees table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS brama.meeting_attendees (
                id SERIAL PRIMARY KEY,
                meeting_id INTEGER REFERENCES brama.meetings(id),
                user_id INTEGER REFERENCES brama.users(id),
                joined_at TIMESTAMP,
                left_at TIMESTAMP
            )
            """)
            print("Table 'meeting_attendees' created.")
            
            # Create meeting_votes table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS brama.meeting_votes (
                id SERIAL PRIMARY KEY,
                agenda_item_id INTEGER REFERENCES brama.agenda_items(id),
                user_id INTEGER REFERENCES brama.users(id),
                vote brama.votetype,
                comment TEXT,
                voted_at TIMESTAMP
            )
            """)
            print("Table 'meeting_votes' created.")
            
            # Create messages table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS brama.messages (
                id SERIAL PRIMARY KEY,
                meeting_id INTEGER REFERENCES brama.meetings(id),
                user_id INTEGER REFERENCES brama.users(id),
                content TEXT NOT NULL,
                created_at TIMESTAMP
            )
            """)
            print("Table 'messages' created.")
            
            # Create meeting_documents table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS brama.meeting_documents (
                id SERIAL PRIMARY KEY,
                meeting_id INTEGER REFERENCES brama.meetings(id),
                name VARCHAR(255) NOT NULL,
                description TEXT,
                file_data BYTEA NOT NULL,
                file_mimetype VARCHAR(128) NOT NULL,
                file_size INTEGER NOT NULL,
                uploaded_by INTEGER REFERENCES brama.users(id),
                uploaded_at TIMESTAMP,
                is_public BOOLEAN
            )
            """)
            print("Table 'meeting_documents' created.")
            
            # Update the alembic version
            cursor.execute("SELECT version_num FROM alembic_version")
            current_version = cursor.fetchone()[0]
            print(f"Current version: {current_version}")
            
            # Check if dabbad00feed is already in the version history
            cursor.execute("SELECT COUNT(*) FROM alembic_version WHERE version_num = 'dabbad00feed'")
            has_version = cursor.fetchone()[0]
            
            if not has_version:
                cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('dabbad00feed')")
                print("Added 'dabbad00feed' to alembic_version table.")
        else:
            print("Tables already exist. Migration is already applied.")
        
        print("Database migration completed successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()