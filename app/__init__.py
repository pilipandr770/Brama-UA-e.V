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

    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    from app.routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    return app
