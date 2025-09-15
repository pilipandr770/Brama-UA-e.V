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
    
    # Engine options только для PostgreSQL
    if os.getenv("DATABASE_URL", "").startswith("postgresql"):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "connect_args": {
                # правильный формат: опция -c и пробел
                "options": f"-c search_path={os.getenv('DB_SCHEMA', 'public')}"
            }
        }
    else:
        SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # Base URL for links in emails
    BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")
    
    # Email configuration
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ("true", "1", "t")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@brama-ua.org")
