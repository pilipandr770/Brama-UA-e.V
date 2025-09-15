#!/bin/bash
# Даємо Flask знати, де знаходиться додаток
export FLASK_APP=run.py
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Запускаємо міграції та додаток
# Try targeted upgrades on the brama branch to avoid multiple-head conflicts
python -m flask db upgrade 31dcbe661936 || echo "Targeted migration 31dcbe661936 failed or already applied"
python -m flask db upgrade b1a2c3d4e5f6 || echo "Targeted migration b1a2c3d4e5f6 failed or already applied"

# Use eventlet worker for Socket.IO compatibility
gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT run:app
