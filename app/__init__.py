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
    
    # Настраиваем расширенное логирование
    if os.getenv("ENHANCED_LOGGING", "true").lower() in ("1", "true", "yes"):
        try:
            from app.enhanced_logging import setup_enhanced_logging
            setup_enhanced_logging(app)
            app.logger.info("Расширенное логирование активировано")
        except Exception as e:
            app.logger.warning(f"Не удалось настроить расширенное логирование: {e}")

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
    
    # Регистрируем тестовые маршруты для отладки ошибок
    if app.debug or app.testing:
        try:
            from app.test_error import register_test_error_routes
            register_test_error_routes(app)
        except ImportError:
            app.logger.warning("Модуль test_error не найден, тестовые маршруты для ошибок не зарегистрированы")

    # Optional: run critical DB migrations on startup (idempotent per revision)
    if os.getenv("AUTO_MIGRATE_ON_START", "true").lower() in ("1", "true", "yes"):  # default on
        try:
            from flask_migrate import upgrade as alembic_upgrade
            with app.app_context():
                for rev in ("31dcbe661935", "31dcbe661936", "b1a2c3d4e5f6", "cafe4dadbeef", "dabbad00feed", 
                           "add_image_data_to_blocks", "add_name_slug_to_blocks", "hotfix_name_slug_blocks"):
                    try:
                        alembic_upgrade(revision=rev)
                    except Exception as mig_err:
                        app.logger.warning(f"Startup migration {rev} skipped or failed: {mig_err}")
                        
            # Применяем дополнительный фикс для таблицы blocks
            from app.database_fix import check_and_fix_blocks_table, monkey_patch_block_model
            check_and_fix_blocks_table(app)  # Проверяем и исправляем структуру таблицы
            monkey_patch_block_model()       # Применяем обходной путь к модели Block
            
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

    # Добавляем расширенную обработку ошибок
    from flask import render_template, request
    import traceback
    
    @app.errorhandler(500)
    def internal_server_error(e):
        error_traceback = traceback.format_exc()
        
        # Используем расширенное логирование, если доступно
        if hasattr(app, 'log_exception'):
            app.log_exception(e, 500)
        else:
            app.logger.error(f"500 Internal Server Error: {error_traceback}")
            
        # Отображаем стандартный шаблон ошибки
        try:
            # Сначала пробуем использовать новый шаблон с base.html
            return render_template('error_base.html', 
                                error_code=500, 
                                error_title="Внутренняя ошибка сервера", 
                                error_message="Произошла внутренняя ошибка при обработке вашего запроса.", 
                                error_details=error_traceback if app.debug else None), 500
        except Exception as base_err:
            app.logger.error(f"Ошибка при рендеринге шаблона error_base.html: {base_err}")
            try:
                # Если не получилось, пробуем использовать автономный error.html
                return render_template('error.html', 
                                    error_code=500, 
                                    error_title="Внутренняя ошибка сервера", 
                                    error_message="Произошла внутренняя ошибка при обработке вашего запроса.", 
                                    error_details=error_traceback if app.debug else None), 500
            except Exception as template_err:
                app.logger.error(f"Ошибка при рендеринге шаблона error.html: {template_err}")
                # Возвращаем простой текст в крайнем случае
                return "Внутренняя ошибка сервера (500). Пожалуйста, обратитесь к администратору.", 500
                              
    @app.errorhandler(404)
    def page_not_found(e):
        # Используем расширенное логирование, если доступно
        if hasattr(app, 'log_exception'):
            app.log_exception(e, 404)
        else:
            app.logger.info(f"404 Not Found: {request.path}")
            
        try:
            # Сначала пробуем использовать новый шаблон с base.html
            return render_template('error_base.html', 
                                error_code=404, 
                                error_title="Страница не найдена",
                                error_message=f"Страница '{request.path}' не найдена."), 404
        except Exception as base_err:
            app.logger.error(f"Ошибка при рендеринге шаблона error_base.html для 404: {base_err}")
            try:
                # Если не получилось, пробуем использовать автономный error.html
                return render_template('error.html', 
                                    error_code=404, 
                                    error_title="Страница не найдена",
                                    error_message=f"Страница '{request.path}' не найдена."), 404
            except Exception as template_err:
                app.logger.error(f"Ошибка при рендеринге шаблона error.html для 404: {template_err}")
                return f"Страница '{request.path}' не найдена (404).", 404
                              
    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        error_traceback = traceback.format_exc()
        
        # Используем расширенное логирование, если доступно
        if hasattr(app, 'log_exception'):
            app.log_exception(e)
        else:
            app.logger.error(f"Unhandled Exception: {error_traceback}")
            
        try:
            # Сначала пробуем использовать новый шаблон с base.html
            return render_template('error_base.html', 
                                error_code=500, 
                                error_title="Ошибка приложения",
                                error_message="Произошла непредвиденная ошибка.", 
                                error_details=error_traceback if app.debug else None), 500
        except Exception as base_err:
            app.logger.error(f"Ошибка при рендеринге шаблона error_base.html для исключения: {base_err}")
            try:
                # Если не получилось, пробуем использовать автономный error.html
                return render_template('error.html', 
                                    error_code=500, 
                                    error_title="Ошибка приложения",
                                    error_message="Произошла непредвиденная ошибка.", 
                                    error_details=error_traceback if app.debug else None), 500
            except Exception as template_err:
                app.logger.error(f"Ошибка при рендеринге шаблона необработанного исключения: {template_err}")
                return "Внутренняя ошибка сервера. Пожалуйста, обратитесь к администратору.", 500

    return app

# Экспортируем переменную app для gunicorn
app = create_app()
