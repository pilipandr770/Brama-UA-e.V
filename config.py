import os
from pathlib import Path

basedir = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Render дає DATABASE_URL для PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")

    if not SQLALCHEMY_DATABASE_URI:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{basedir / 'site.db'}"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    BABEL_DEFAULT_LOCALE = 'uk'
    # Engine options to select schema via DB_SCHEMA env var
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            # правильный формат: опция -c и пробел
            "options": f"-c search_path={os.getenv('DB_SCHEMA', 'public')}"
        }
    }
