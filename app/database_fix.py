"""
Обходной путь для исправления проблем со схемой БД при запуске.
"""

from flask import Flask
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError
import os
import logging

logger = logging.getLogger('app.database_fix')

def check_and_fix_blocks_table(app: Flask):
    """
    Проверяет и исправляет структуру таблицы blocks перед запуском приложения.
    Добавляет отсутствующие поля name и slug.
    """
    try:
        # Получаем URL базы данных из конфига
        db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
        if not db_url:
            logger.error("Database URL not found in app configuration")
            return
        
        # Создаем движок для прямого доступа к базе данных
        engine = create_engine(db_url)
        
        # Проверяем наличие необходимых столбцов
        with engine.connect() as conn:
            inspector = inspect(engine)
            columns = [c['name'] for c in inspector.get_columns('blocks', schema='brama')]
            
            # Если таблица не имеет необходимых столбцов, добавляем их
            if 'name' not in columns:
                logger.info("Column 'name' missing from blocks table, adding it...")
                try:
                    conn.execute(text("ALTER TABLE brama.blocks ADD COLUMN name VARCHAR(50) DEFAULT 'legacy';"))
                    conn.execute(text("UPDATE brama.blocks SET name = 'legacy' WHERE name IS NULL;"))
                    conn.commit()
                    logger.info("Added column 'name' to blocks table")
                except SQLAlchemyError as e:
                    logger.error(f"Failed to add column 'name': {e}")
            
            if 'slug' not in columns:
                logger.info("Column 'slug' missing from blocks table, adding it...")
                try:
                    conn.execute(text("ALTER TABLE brama.blocks ADD COLUMN slug VARCHAR(50);"))
                    conn.commit()
                    logger.info("Added column 'slug' to blocks table")
                except SQLAlchemyError as e:
                    logger.error(f"Failed to add column 'slug': {e}")
            
    except Exception as e:
        logger.error(f"Error checking/fixing blocks table: {e}")
        
# Монки-патч для Block модели для обхода отсутствующих полей
def monkey_patch_block_model():
    """
    Добавляет динамические свойства в модель Block, позволяя
    работать даже при отсутствии полей name и slug в БД.
    """
    from app.models.block import Block
    
    # Динамически модифицируем класс Block для работы без полей name и slug
    if not hasattr(Block, '_patched'):
        # Добавляем флаг, чтобы избежать повторного патчинга
        Block._patched = True
        
        # Оригинальная функция __init__
        orig_init = Block.__init__
        
        # Новая функция __init__ для обхода проблем с отсутствующими полями
        def safe_init(self, **kwargs):
            try:
                # Вызываем оригинальный __init__
                orig_init(self, **kwargs)
            except Exception as e:
                # Если возникла ошибка, пробуем инициализировать только безопасные поля
                safe_kwargs = {k: v for k, v in kwargs.items() 
                              if k in ('id', 'title', 'content', 'type', 'is_active', 
                                      'image_url', 'translations')}
                super(Block, self).__init__(**safe_kwargs)
                logger.warning(f"Block initialized with limited fields due to error: {e}")
        
        # Заменяем оригинальный __init__
        Block.__init__ = safe_init