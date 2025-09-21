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
    Добавляет отсутствующие поля name, slug, image_data и image_mimetype.
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
            
            # Пробуем разные схемы базы данных
            columns = []
            schema_name = None
            
            # Пробуем с схемой brama
            try:
                columns = [c['name'] for c in inspector.get_columns('blocks', schema='brama')]
                schema_name = 'brama'
            except SQLAlchemyError:
                # Пробуем без схемы (для SQLite)
                try:
                    columns = [c['name'] for c in inspector.get_columns('blocks')]
                    schema_name = None
                except SQLAlchemyError as e:
                    logger.error(f"Could not inspect blocks table: {e}")
                    return
            
            # Формируем ссылку на таблицу с учетом схемы
            table_ref = f"{schema_name}.blocks" if schema_name else "blocks"
            
            # Словарь отсутствующих колонок и их типов
            missing_columns = {
                'name': "VARCHAR(50) DEFAULT 'legacy'",
                'slug': "VARCHAR(50)",
                'image_data': "BYTEA" if 'postgresql' in db_url.lower() else "BLOB",  # PostgreSQL использует BYTEA, SQLite использует BLOB
                'image_mimetype': "VARCHAR(64)"
            }
            
            # Проверяем и добавляем отсутствующие столбцы
            for col_name, col_type in missing_columns.items():
                if col_name not in columns:
                    logger.info(f"Column '{col_name}' missing from blocks table, adding it...")
                    try:
                        # SQLite синтаксис отличается от PostgreSQL
                        if 'sqlite' in db_url.lower():
                            conn.execute(text(f"ALTER TABLE blocks ADD COLUMN {col_name} {col_type};"))
                            conn.commit()
                        else:
                            # В PostgreSQL выполняем каждое изменение в отдельной транзакции
                            # чтобы избежать проблем с прерванными транзакциями
                            with engine.begin() as transaction:
                                transaction.execute(text(f"ALTER TABLE {table_ref} ADD COLUMN {col_name} {col_type};"))
                        
                        # Если это имя, заполняем его значением по умолчанию в отдельной транзакции
                        if col_name == 'name':
                            if 'sqlite' in db_url.lower():
                                conn.execute(text(f"UPDATE blocks SET name = 'legacy' WHERE name IS NULL;"))
                                conn.commit()
                            else:
                                with engine.begin() as transaction:
                                    transaction.execute(text(f"UPDATE {table_ref} SET name = 'legacy' WHERE name IS NULL;"))
                        
                        # Если это slug, генерируем его на основе id в отдельной транзакции
                        if col_name == 'slug':
                            if 'sqlite' in db_url.lower():
                                conn.execute(text(f"UPDATE blocks SET slug = 'block_' || id WHERE slug IS NULL;"))
                                conn.commit()
                            else:
                                with engine.begin() as transaction:
                                    transaction.execute(text(f"UPDATE {table_ref} SET slug = 'block_' || id WHERE slug IS NULL;"))
                        
                        logger.info(f"Added column '{col_name}' to blocks table")
                    except SQLAlchemyError as e:
                        logger.error(f"Failed to add column '{col_name}': {e}")
                        if 'sqlite' not in db_url.lower():
                            # Для PostgreSQL попытаемся сбросить состояние транзакции
                            try:
                                conn.execute(text("ROLLBACK;"))
                            except:
                                pass
            
    except Exception as e:
        logger.error(f"Error checking/fixing blocks table: {e}")
        
# Монки-патч для Block модели для обхода отсутствующих полей
def monkey_patch_block_model():
    """
    Этот метод больше не нужен, так как модель Block теперь содержит
    правильную реализацию с использованием __declare_last__ и db.deferred.
    Оставлен для обратной совместимости с существующим кодом.
    """
    from app.models.block import Block
    
    # Добавляем флаг, показывающий что новая модель Block уже обрабатывает всё корректно
    if not hasattr(Block, '_patched'):
        Block._patched = True
        logger.info("Block model now uses deferred loading and __declare_last__, no monkey patching needed")


def check_and_fix_projects_table(app: Flask):
    """
    Проверяет и исправляет структуру таблицы projects перед запуском приложения.
    Добавляет отсутствующие поля document_url, image_data и image_mimetype.
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
            
            # Пробуем разные схемы базы данных
            columns = []
            schema_name = None
            
            # Пробуем с схемой brama
            try:
                columns = [c['name'] for c in inspector.get_columns('projects', schema='brama')]
                schema_name = 'brama'
            except SQLAlchemyError:
                # Пробуем без схемы (для SQLite)
                try:
                    columns = [c['name'] for c in inspector.get_columns('projects')]
                    schema_name = None
                except SQLAlchemyError as e:
                    logger.error(f"Could not inspect projects table: {e}")
                    return
            
            # Формируем ссылку на таблицу с учетом схемы
            table_ref = f"{schema_name}.projects" if schema_name else "projects"
            
            # Словарь отсутствующих колонок и их типов
            missing_columns = {
                'document_url': "VARCHAR(300)",
                'image_data': "BYTEA" if 'postgresql' in db_url.lower() else "BLOB",  # PostgreSQL использует BYTEA, SQLite использует BLOB
                'image_mimetype': "VARCHAR(64)"
            }
            
            # Проверяем и добавляем отсутствующие столбцы
            for col_name, col_type in missing_columns.items():
                if col_name not in columns:
                    logger.info(f"Column '{col_name}' missing from projects table, adding it...")
                    try:
                        # SQLite синтаксис отличается от PostgreSQL
                        if 'sqlite' in db_url.lower():
                            conn.execute(text(f"ALTER TABLE projects ADD COLUMN {col_name} {col_type};"))
                            conn.commit()
                        else:
                            # В PostgreSQL выполняем каждое изменение в отдельной транзакции
                            # чтобы избежать проблем с прерванными транзакциями
                            with engine.begin() as transaction:
                                transaction.execute(text(f"ALTER TABLE {table_ref} ADD COLUMN {col_name} {col_type};"))
                        
                        logger.info(f"Added column '{col_name}' to projects table")
                    except SQLAlchemyError as e:
                        logger.error(f"Failed to add column '{col_name}': {e}")
                        if 'sqlite' not in db_url.lower():
                            # Для PostgreSQL попытаемся сбросить состояние транзакции
                            try:
                                conn.execute(text("ROLLBACK;"))
                            except:
                                pass
            
    except Exception as e:
        logger.error(f"Error checking/fixing projects table: {e}")