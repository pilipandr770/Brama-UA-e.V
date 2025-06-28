# Порожній файл, але потрібен для імпорту blueprint'ів
from app.routes.main import main_bp as main
from app.routes.admin import admin_bp as admin
from app.routes.api import api_bp as api
from app.routes.brama import brama_bp
from app.routes.founder import founder_bp as founder
from app.routes.language import language_bp as language
from app.routes.multilingual import multilingual_bp as multilingual
from app.routes.multilingual_admin import multilingual_admin_bp as multilingual_admin

def register_blueprints(app):
    """Регистрация всех blueprints приложения"""
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(api)
    app.register_blueprint(brama_bp)
    app.register_blueprint(founder)
    app.register_blueprint(language)
    app.register_blueprint(multilingual)
    app.register_blueprint(multilingual_admin)
