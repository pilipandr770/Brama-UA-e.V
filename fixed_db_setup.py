from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_login import LoginManager
from dotenv import load_dotenv
import os
from datetime import datetime

# Создаём временный файл для инициализации базы данных без опций
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
login_manager = LoginManager()

# Путь к базе данных
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
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
    translations = db.Column(db.JSON)

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    
    id = db.Column(db.Integer, primary_key=True)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(300))
    image_data = db.Column(db.LargeBinary)
    image_mimetype = db.Column(db.String(100))
    translations = db.Column(db.JSON)

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), default="Brama UA e.V.")
    site_description = db.Column(db.Text)
    contact_email = db.Column(db.String(120))
    facebook = db.Column(db.String(200))
    instagram = db.Column(db.String(200))
    telegram = db.Column(db.String(200))
    translations = db.Column(db.JSON)

class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem_description = db.Column(db.Text, nullable=True)
    goal = db.Column(db.Text, nullable=True)
    target_audience = db.Column(db.Text, nullable=True)
    implementation_plan = db.Column(db.Text, nullable=True)
    executor_info = db.Column(db.Text, nullable=True)
    total_budget = db.Column(db.Float, nullable=True)
    budget_breakdown = db.Column(db.Text, nullable=True)
    expected_result = db.Column(db.Text, nullable=True)
    risks = db.Column(db.Text, nullable=True)
    duration = db.Column(db.String(100), nullable=True)
    reporting_plan = db.Column(db.Text, nullable=True)
    
    # Додаткові поля
    category = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    social_links = db.Column(db.Text)  # JSON рядок або список через кому
    image_url = db.Column(db.String(300), nullable=True)
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_mimetype = db.Column(db.String(64), nullable=True)
    status = db.Column(db.String(20), default='pending')
    user_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'), nullable=True)

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
        contact_email='contact@brama-ua.org',
        facebook='https://facebook.com/bramaua',
        instagram='https://instagram.com/brama_ua',
        telegram='https://t.me/brama_ua'
    )
    db.session.add(settings)
    
    info_block = Block(
        title='Про нас',
        content='Brama UA - це об\'єднання українців у Німеччині, яке допомагає розвивати культурні та економічні зв\'язки.',
        type='info',
        is_active=True
    )
    db.session.add(info_block)
    
    gallery_block = Block(
        title='Галерея',
        content='Фотографії з наших заходів та проєктів.',
        type='gallery',
        is_active=True
    )
    db.session.add(gallery_block)
    
    projects_block = Block(
        title='Проєкти',
        content='Наші активні та завершені проєкти.',
        type='projects',
        is_active=True
    )
    db.session.add(projects_block)
    
    # Добавляем тестовый проект
    project = Project(
        title='Тестовий проект',
        problem_description='Опис проблеми, яку вирішує проект',
        goal='Мета проекту',
        target_audience='Цільова аудиторія',
        implementation_plan='План реалізації проекту',
        executor_info='Інформація про виконавця',
        total_budget=5000.0,
        budget_breakdown='Розбивка бюджету',
        expected_result='Очікуваний результат',
        risks='Можливі ризики',
        duration='3 місяці',
        reporting_plan='План звітності',
        category='Культура',
        location='Берлін',
        status='approved',
        user_id=2,  # ID обычного пользователя
        block_id=3  # ID блока проектов
    )
    db.session.add(project)
    
    # Сохраняем изменения
    db.session.commit()
    
    print(f"База данных успешно создана по пути: {db_path}")
    print("Добавлены тестовые данные:")
    print("- Admin пользователь (admin@example.com / adminpassword)")
    print("- Regular пользователь (user@example.com / userpassword)")
    print("- Настройки сайта")
    print("- Блоки контента (info, gallery, projects)")
    print("- Тестовый проект в статусе 'approved'")
