from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from pathlib import Path

app = Flask(__name__)

# Путь из config.py
basedir = Path(__file__).resolve().parent
db_path1 = basedir / 'site.db'
print(f"Путь 1 (config.py): {db_path1}")
print(f"Существует файл по пути 1: {os.path.exists(db_path1)}")

# Альтернативный путь
basedir2 = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_path2 = os.path.join(basedir2, 'site.db')
print(f"Путь 2 (родительская директория): {db_path2}")
print(f"Существует файл по пути 2: {os.path.exists(db_path2)}")

# Путь из local_db_setup.py
basedir3 = os.path.abspath(os.path.dirname(__file__))
db_path3 = os.path.join(basedir3, 'site.db')
print(f"Путь 3 (текущая директория): {db_path3}")
print(f"Существует файл по пути 3: {os.path.exists(db_path3)}")

# Проверка используемого пути в конфигурации
from config import Config
print(f"SQLALCHEMY_DATABASE_URI из config.py: {Config.SQLALCHEMY_DATABASE_URI}")
