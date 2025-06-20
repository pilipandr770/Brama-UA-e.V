import logging
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
from app import db

# Alembic Config object
config = context.config

# Set up loggers
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')

target_metadata = db.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Використовуємо URL з env або з alembic.ini
    import os
    url = os.environ.get('DATABASE_URL', config.get_main_option('sqlalchemy.url'))
    
    # Якщо URL починається з postgres:// замінюємо на postgresql://
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
        
    connectable = engine_from_config(
        {"url": url},
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
