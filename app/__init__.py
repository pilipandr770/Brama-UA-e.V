from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_babel import Babel
from dotenv import load_dotenv
import os

db = SQLAlchemy()
migrate = Migrate()
babel = Babel()

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app)

    # Используем централизованную регистрацию blueprints
    from app.routes import register_blueprints
    register_blueprints(app)

    @app.context_processor
    def inject_settings():
        from app.models.settings import Settings
        settings = Settings.query.first()
        return dict(settings=settings)

    return app
