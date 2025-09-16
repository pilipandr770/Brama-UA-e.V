"""
Скрипт для тестирования обработки ошибок и логирования в приложении.

Этот скрипт добавляет временные маршруты для тестирования различных типов ошибок.
В продакшн версии его следует деактивировать.
"""

from flask import Blueprint, abort, current_app

# Создаем Blueprint для тестовых маршрутов
test_error_bp = Blueprint('test_error', __name__)

@test_error_bp.route('/test-404')
def test_404():
    """Тест для страницы 404"""
    current_app.logger.info("Тестирование ошибки 404")
    abort(404)

@test_error_bp.route('/test-500')
def test_500():
    """Тест для страницы 500"""
    current_app.logger.info("Тестирование ошибки 500")
    abort(500)

@test_error_bp.route('/test-exception')
def test_exception():
    """Тест для необработанного исключения"""
    current_app.logger.info("Тестирование необработанного исключения")
    # Намеренно вызываем исключение
    raise Exception("Тестовое исключение")

@test_error_bp.route('/test-render-error')
def test_render_error():
    """Тест для ошибки рендеринга шаблона"""
    current_app.logger.info("Тестирование ошибки рендеринга шаблона")
    # Используем несуществующую переменную в шаблоне
    return current_app.render_template('base.html', 
                                      nonexistent_variable=nonexistent_variable)

def register_test_error_routes(app):
    """Регистрирует тестовые маршруты в приложении, только если включен режим отладки"""
    if app.debug or app.config.get('TESTING', False):
        app.register_blueprint(test_error_bp, url_prefix='/test')
        app.logger.info("Зарегистрированы тестовые маршруты для проверки ошибок")