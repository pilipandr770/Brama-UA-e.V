import sys
from pathlib import Path
# Add project root to PYTHONPATH so 'app' package is found
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import os
from app import create_app, db

# Получаем схему из переменной окружения
schema = os.getenv('DB_SCHEMA', 'public')
print(f"Creating tables in schema '{schema}'...")

# Создаем приложение и инициализируем DB
app = create_app()
with app.app_context():
    # Debugging: вывести текущий DB URI и схему
    print("SQLALCHEMY_DATABASE_URI:", app.config.get('SQLALCHEMY_DATABASE_URI'))
    print("DB_SCHEMA:", os.getenv('DB_SCHEMA'))
    db.create_all()
    print("Tables created.")
