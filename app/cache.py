"""
Модуль для кэширования и оптимизации загрузки контента.
Добавляет механизмы кэширования для наиболее часто используемых ресурсов.
"""
from flask import Flask
from flask_caching import Cache

cache = Cache()

def init_cache(app: Flask):
    """
    Инициализирует кэширование для приложения Flask
    """
    cache_config = {
        'CACHE_TYPE': 'SimpleCache',  # Простой кэш в памяти
        'CACHE_DEFAULT_TIMEOUT': 300,  # 5 минут
        'CACHE_THRESHOLD': 1000,       # Максимальное количество объектов в кэше
    }
    app.config.from_mapping(cache_config)
    cache.init_app(app)
    
    # Регистрируем функцию для очистки кэша при запуске сервера
    with app.app_context():
        cache.clear()
        app.logger.info("Кэш инициализирован и очищен")

    return cache