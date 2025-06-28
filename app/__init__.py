from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()

# Import our babel setup (needs to be after initializing the other extensions)
from app.babel import init_babel

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    init_babel(app)  # Initialize Babel with our custom locale selector
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Configure Babel settings
    app.config['BABEL_DEFAULT_LOCALE'] = 'uk'
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'Europe/Kyiv'
    app.config['LANGUAGES'] = {
        'uk': 'Українська',
        'de': 'Deutsch',
        'en': 'English'
    }

    # Используем централизованную регистрацию blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    @app.context_processor
    def inject_settings():
        from app.models.settings import Settings
        settings = Settings.query.first()
        return dict(settings=settings)
    
    # Import WebSocket handlers
    with app.app_context():
        from app import websockets

    return app
