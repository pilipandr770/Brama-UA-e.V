"""
This script applies manual fixes to the database to handle migration issues
with the existing votes table and the new meeting_votes table.
"""

import os
import sys
from sqlalchemy import text
from app import db, create_app

app = create_app()

def apply_manual_migration():
    with app.app_context():
        with open('migrations/manual_fix.sql', 'r') as f:
            sql = f.read()
        
        try:
            # Execute the SQL statements
            conn = db.engine.connect()
            conn.execute(text(sql))
            conn.commit()
            conn.close()
            print("✅ Manual database fixes applied successfully!")
        except Exception as e:
            print(f"❌ Error applying manual fixes: {e}")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(apply_manual_migration())
