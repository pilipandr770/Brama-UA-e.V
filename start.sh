#!/bin/bash
# Даємо Flask знати, де знаходиться додаток
export FLASK_APP=run.py
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Запускаємо міграції та додаток

set -euo pipefail

# 1) Environment setup
export FLASK_APP=run.py
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

echo "[start.sh] Python version: $(python --version 2>&1)"
echo "[start.sh] Pip version: $(pip --version 2>&1)"
echo "[start.sh] FLASK_APP=${FLASK_APP}"
echo "[start.sh] DB_SCHEMA=${DB_SCHEMA:-not-set}"

# 2) Database migrations (run in strict order)
echo "[start.sh] Applying Alembic migrations (targeted sequence)"
flask db upgrade 31dcbe661935 || echo "[start.sh] Migration 31dcbe661935 already applied or not required"
flask db upgrade 31dcbe661936 || echo "[start.sh] Migration 31dcbe661936 already applied or not required"
flask db upgrade b1a2c3d4e5f6 || echo "[start.sh] Migration b1a2c3d4e5f6 already applied or not required"
flask db upgrade cafe4dadbeef || echo "[start.sh] Migration cafe4dadbeef already applied or not required"
flask db upgrade dabbad00feed || echo "[start.sh] Migration dabbad00feed already applied or not required"
flask db upgrade add_image_data_to_blocks || echo "[start.sh] Migration add_image_data_to_blocks already applied or not required"
flask db upgrade add_name_slug_to_blocks || echo "[start.sh] Migration add_name_slug_to_blocks already applied or not required"
flask db upgrade hotfix_name_slug_blocks || echo "[start.sh] Migration hotfix_name_slug_blocks already applied or not required"

# Применяем все оставшиеся миграции (включая новые)
echo "[start.sh] Applying all remaining migrations..."
flask db upgrade head || echo "[start.sh] Error applying migrations, but continuing..."

# Автоматически выполняем SQL для исправления структуры таблицы blocks
echo "[start.sh] Применяем прямое SQL-исправление для таблицы blocks..."
psql "$DATABASE_URL" -c "ALTER TABLE brama.blocks ADD COLUMN IF NOT EXISTS name VARCHAR(50) DEFAULT 'legacy';" || echo "[start.sh] Couldn't add name column, may already exist"
psql "$DATABASE_URL" -c "ALTER TABLE brama.blocks ADD COLUMN IF NOT EXISTS slug VARCHAR(50);" || echo "[start.sh] Couldn't add slug column, may already exist"
psql "$DATABASE_URL" -c "UPDATE brama.blocks SET name = 'legacy' WHERE name IS NULL;" || echo "[start.sh] Couldn't update NULL names"

# 3) Start the app with sync workers (no Socket.IO)
echo "[start.sh] Starting Gunicorn with sync workers"

# Вычисляем количество воркеров (2 * CPU + 1) или минимум 3
NUM_WORKERS=${WEB_CONCURRENCY:-3}  # По умолчанию используем 3 воркера

# Настройки таймаута
TIMEOUT=${GUNICORN_TIMEOUT:-60}  # 60 секунд таймаута для воркеров
KEEPALIVE=${GUNICORN_KEEPALIVE:-5}  # 5 секунд keepalive для соединений

# Запускаем с sync workers (без Socket.IO/eventlet)
exec gunicorn --worker-class sync \
    --workers $NUM_WORKERS \
    --timeout $TIMEOUT \
    --keep-alive $KEEPALIVE \
    --log-level info \
    --access-logfile - \
    --error-logfile - \
    --bind 0.0.0.0:$PORT \
    run:app
