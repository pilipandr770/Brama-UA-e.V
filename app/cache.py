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

# Функции для кэширования часто используемых данных

@cache.memoize(timeout=600)  # Кэш на 10 минут
def get_active_blocks():
    """Кэшированная функция для получения всех активных блоков"""
    from app.models.block import Block
    return Block.query.filter_by(is_active=True).all()

@cache.memoize(timeout=300)  # Кэш на 5 минут
def get_block_by_type(block_type):
    """Кэшированная функция для получения блока по типу"""
    from app.models.block import Block
    return Block.query.filter_by(type=block_type, is_active=True).first()

@cache.memoize(timeout=300)  # Кэш на 5 минут
def get_gallery_images(block_id):
    """Кэшированная функция для получения изображений галереи"""
    from app.models.gallery_image import GalleryImage
    return GalleryImage.query.filter_by(block_id=block_id).all()

@cache.memoize(timeout=180)  # Кэш на 3 минуты
def get_approved_projects(block_id):
    """Кэшированная функция для получения одобренных проектов"""
    from app.models.project import Project
    return Project.query.filter_by(status='approved', block_id=block_id).order_by(Project.created_at.desc()).all()

@cache.memoize(timeout=3600)  # Кэш на 1 час
def get_settings():
    """Кэшированная функция для получения настроек"""
    from app.models.settings import Settings
    return Settings.query.first()