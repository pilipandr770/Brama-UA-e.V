from app import create_app, db
import sys
from sqlalchemy.sql import text

app = create_app()

with app.app_context():
    try:
        # Add profile_photo_url column to users table if it doesn't exist
        db.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(300);"))
        db.session.commit()
        print("Successfully added profile_photo_url column to users table")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
