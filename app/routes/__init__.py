# Порожній файл, але потрібен для імпорту blueprint'ів
from app.routes.main import main_bp as main
from app.routes.admin import admin_bp as admin
from app.routes.api import api_bp as api
from app.routes.brama import brama_bp
from app.routes.founder import founder_bp as founder

def register_blueprints(app):
    """Регистрация всех blueprints приложения"""
    app.register_blueprint(main)
    app.register_blueprint(admin)
    app.register_blueprint(api)
    app.register_blueprint(brama_bp)
    app.register_blueprint(founder)
