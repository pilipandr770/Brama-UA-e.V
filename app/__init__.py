from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_login import LoginManager
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
login_manager = LoginManager()

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
    
    # Настраиваем Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Будь ласка, увійдіть для доступу до цієї сторінки.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return User.query.get(int(user_id))
    
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

    # Optional: run critical DB migrations on startup (idempotent per revision)
    if os.getenv("AUTO_MIGRATE_ON_START", "true").lower() in ("1", "true", "yes"):  # default on
        try:
            from flask_migrate import upgrade as alembic_upgrade
            with app.app_context():
                for rev in ("31dcbe661935", "31dcbe661936", "b1a2c3d4e5f6"):
                    try:
                        alembic_upgrade(rev)
                    except Exception as mig_err:
                        app.logger.warning(f"Startup migration {rev} skipped or failed: {mig_err}")
        except Exception as e:
            app.logger.warning(f"AUTO_MIGRATE_ON_START failed to run: {e}")

    @app.context_processor
    def inject_settings():
        from app.models.settings import Settings
        settings = Settings.query.first()
        
        # Для обратной совместимости добавим user в контекст
        from flask_login import current_user
        user = None
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
            user = current_user
            
        return dict(settings=settings, user=user)
    
    # Import WebSocket handlers
    with app.app_context():
        from app import websockets


    return app

# Экспортируем переменную app для gunicorn
app = create_app()
