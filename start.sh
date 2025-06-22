#!/bin/bash
# Даємо Flask знати, де знаходиться додаток
export FLASK_APP=run.py
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# Запускаємо міграції та додаток
python -m flask db upgrade || echo "Migration failed but continuing with application startup"
gunicorn --bind 0.0.0.0:$PORT run:app
