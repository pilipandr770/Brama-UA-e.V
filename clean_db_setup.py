from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Создаём временный файл для инициализации базы данных без опций
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
login_manager = LoginManager()

# Путь к базе данных
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'site.db')

# Создаём приложение
app = Flask(__name__)
app.config['SECRET_KEY'] = 'local-dev-key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db.init_app(app)

# Определение моделей
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    birth_date = db.Column(db.Date)
    specialty = db.Column(db.String(128))
    join_goal = db.Column(db.String(256))
    can_help = db.Column(db.String(256))
    want_to_do = db.Column(db.String(256))
    phone = db.Column(db.String(32))
    is_member = db.Column(db.Boolean, default=True)
    is_founder = db.Column(db.Boolean, default=False)
    consent_given = db.Column(db.Boolean, default=False)
    contributions = db.Column(db.Float, default=0.0)
    profile_photo_url = db.Column(db.String(300), nullable=True)

class Block(db.Model):
    __tablename__ = 'blocks'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300))
    translations = db.Column(db.Text, nullable=True)

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    
    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    image_data = db.Column(db.LargeBinary)
    image_mimetype = db.Column(db.String(100))
    translations = db.Column(db.Text, nullable=True)

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default="Brama UA e.V.")
    site_description = db.Column(db.Text)
    email = db.Column(db.String(256))
    facebook = db.Column(db.String(256))
    instagram = db.Column(db.String(256))
    telegram = db.Column(db.String(256))
    translations = db.Column(db.Text, nullable=True)
    
class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)
    goal = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.Text, nullable=False)
    implementation_plan = db.Column(db.Text, nullable=False)
    executor_info = db.Column(db.Text, nullable=False)
    total_budget = db.Column(db.Float, nullable=False)
    budget_breakdown = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)
    risks = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    reporting_plan = db.Column(db.Text, nullable=False)
    
    # Додаткові поля
    category = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    social_links = db.Column(db.Text)  # JSON рядок або список через кому
    image_url = db.Column(db.String(300), nullable=True)
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_mimetype = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(20), default='pending')
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=True)

class Vote(db.Model):
    __tablename__ = 'votes'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Создаём таблицы и тестовые данные
with app.app_context():
    # Удаляем существующую базу данных, если она есть
    if os.path.exists(db_path):
        os.remove(db_path)
    
    # Создаем новые таблицы
    db.create_all()
    
    # Добавляем тестовые данные
    admin = User(
        email='admin@example.com',
        password_hash='pbkdf2:sha256:260000$gZDhk0Qp$842d07e76bd480bd649cae84121714f2c39bb75c8533c4a218520cdb54cdbe10', # adminpassword
        first_name='Admin',
        last_name='User',
        is_admin=True,
        is_member=True,
        consent_given=True
    )
    db.session.add(admin)
    
    user = User(
        email='user@example.com',
        password_hash='pbkdf2:sha256:260000$weoSKRzp$7bb4579d82142edcd2eea14cf2dad69b5970754243799f49b702e0b5fc7c8c1e', # userpassword
        first_name='Regular',
        last_name='User',
        is_admin=False,
        is_member=True,
        consent_given=True
    )
    db.session.add(user)
    
    settings = Settings(
        site_name='Brama UA e.V.',
        site_description='Українське об\'єднання в Німеччині',
        email='contact@brama-ua.org',
        facebook='https://facebook.com/bramaua',
        instagram='https://instagram.com/brama_ua',
        telegram='https://t.me/brama_ua',
        translations=json.dumps({
            "en": {
                "site_description": "Ukrainian Association in Germany"
            },
            "de": {
                "site_description": "Ukrainischer Verein in Deutschland"
            }
        })
    )
    db.session.add(settings)
    
    info_block = Block(
        title='Про нас',
        content='Brama UA - це об\'єднання українців у Німеччині, яке допомагає розвивати культурні та економічні зв\'язки.',
        type='info',
        is_active=True,
        translations=json.dumps({
            "en": {
                "title": "About Us",
                "content": "Brama UA is a Ukrainian association in Germany that helps develop cultural and economic ties."
            },
            "de": {
                "title": "Über uns",
                "content": "Brama UA ist ein ukrainischer Verein in Deutschland, der zur Entwicklung kultureller und wirtschaftlicher Beziehungen beiträgt."
            }
        })
    )
    db.session.add(info_block)
    
    gallery_block = Block(
        title='Галерея',
        content='Фотографії з наших заходів та проєктів.',
        type='gallery',
        is_active=True,
        translations=json.dumps({
            "en": {
                "title": "Gallery",
                "content": "Photos from our events and projects."
            },
            "de": {
                "title": "Galerie",
                "content": "Fotos von unseren Veranstaltungen und Projekten."
            }
        })
    )
    db.session.add(gallery_block)
    
    projects_block = Block(
        title='Проєкти',
        content='Наші активні та завершені проєкти.',
        type='projects',
        is_active=True,
        translations=json.dumps({
            "en": {
                "title": "Projects",
                "content": "Our active and completed projects."
            },
            "de": {
                "title": "Projekte",
                "content": "Unsere aktiven und abgeschlossenen Projekte."
            }
        })
    )
    db.session.add(projects_block)
    
    # Добавляем тестовый проект
    test_project = Project(
        title='Тестовий проект',
        problem_description='Опис проблеми, яку вирішує проект.',
        goal='Мета проекту - допомогти громаді.',
        target_audience='Українці в Німеччині',
        implementation_plan='План реалізації проекту.',
        executor_info='Інформація про виконавців.',
        total_budget=5000.00,
        budget_breakdown='Розподіл бюджету по категоріях.',
        expected_result='Очікувані результати проекту.',
        risks='Можливі ризики та шляхи їх подолання.',
        duration='3 місяці',
        reporting_plan='План звітності.',
        category='Культура',
        location='Берлін',
        user_id=1,  # Admin user
        status='approved',
        block_id=3  # projects block
    )
    db.session.add(test_project)

    # Сохраняем изменения
    db.session.commit()
    
    print(f"База данных успешно создана по пути: {db_path}")
    print("Добавлены тестовые данные:")
    print("- Admin пользователь (admin@example.com / adminpassword)")
    print("- Regular пользователь (user@example.com / userpassword)")
    print("- Настройки сайта")
    print("- Блоки контента (info, gallery, projects)")
    print("- Тестовый проект")
