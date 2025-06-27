from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel
from flask_socketio import SocketIO
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()
babel = Babel()
socketio = SocketIO()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")

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
