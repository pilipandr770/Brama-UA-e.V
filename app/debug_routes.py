"""
Модуль для отладки приложения в продакшн среде.
Создает специальные маршруты, доступные только когда DEBUG_ROUTES=true 
в переменных среды.
"""

from flask import Blueprint, current_app, jsonify
import sys
import os
import traceback

debug_bp = Blueprint('debug', __name__, url_prefix='/debug')

@debug_bp.before_request
def check_debug_enabled():
    """
    Проверяет, включен ли режим отладки для этих маршрутов.
    Доступ разрешен только если установлена переменная среды DEBUG_ROUTES=true.
    """
    from flask import abort
    if os.environ.get('DEBUG_ROUTES', '').lower() != 'true':
        current_app.logger.warning("Попытка доступа к отладочным маршрутам при отключенном DEBUG_ROUTES")
        abort(404)

@debug_bp.route('/info')
def debug_info():
    """
    Возвращает отладочную информацию о приложении.
    """
    info = {
        'python_version': sys.version,
        'env_vars': {k: v for k, v in os.environ.items() if 'SECRET' not in k.upper()},
        'app_config': {k: str(v) for k, v in current_app.config.items() if 'SECRET' not in k.upper()},
        'logger_handlers': str([type(h).__name__ for h in current_app.logger.handlers]),
        'debug_mode': current_app.debug,
        'testing_mode': current_app.testing
    }
    return jsonify(info)

@debug_bp.route('/test-error')
def test_error():
    """
    Вызывает тестовую ошибку для проверки обработки ошибок.
    """
    try:
        # Намеренно вызываем исключение
        1 / 0
    except Exception as e:
        current_app.logger.error(f"Test Error: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        raise

@debug_bp.route('/translations')
def test_translations():
    """
    Тестирует работу переводов на разных языках.
    """
    from flask_babel import gettext as _
    from flask import session

    # Test current translations
    translations = {
        'current_locale': str(session.get('language', 'default')),
        'impressum': _('Impressum'),
        'agb': _('AGB'),
        'datenschutz': _('Datenschutz'),
        'agb_title': _('AGB'),
        'agb_section1': _('1. Geltungsbereich'),
        'agb_section2': _('2. Nutzung der Website')
    }

    # Test with English locale
    session['language'] = 'en'
    translations['en'] = {
        'impressum': _('Impressum'),
        'agb': _('AGB'),
        'datenschutz': _('Datenschutz'),
        'agb_title': _('AGB'),
        'agb_section1': _('1. Geltungsbereich'),
        'agb_section2': _('2. Nutzung der Website')
    }

    # Reset to default
    if 'language' in session:
        del session['language']

    return jsonify(translations)

def register_debug_routes(app):
    """
    Регистрирует отладочные маршруты.
    """
    app.register_blueprint(debug_bp)
    app.logger.info("Отладочные маршруты зарегистрированы. Доступны при DEBUG_ROUTES=true")