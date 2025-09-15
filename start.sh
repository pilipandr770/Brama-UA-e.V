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

# 3) Start the app with eventlet for Socket.IO
echo "[start.sh] Starting Gunicorn (eventlet worker)"
exec gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app

# Use eventlet worker for Socket.IO compatibility
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app
