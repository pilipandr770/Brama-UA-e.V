import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

# Убедимся, что мы используем SQLite
os.environ["DATABASE_URL"] = "sqlite:///site.db"
os.environ["SECRET_KEY"] = "local-dev-key"

# Создаем экземпляры расширений без привязки к приложению
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Создаем приложение Flask
app = Flask(__name__)

# Настраиваем приложение
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

# Инициализируем расширения
db.init_app(app)
migrate.init_app(app, db)
login_manager.init_app(app)

# Определяем основные модели
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
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

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

# Создаем таблицы и тестовые данные
with app.app_context():
    db.create_all()
    
    # Проверяем, есть ли уже пользователи
    if User.query.count() == 0:
        # Создаем администратора
        admin = User(
            email='admin@example.com',
            first_name='Admin',
            last_name='User',
            is_admin=True,
            is_member=True,
            consent_given=True
        )
        admin.set_password('adminpassword')
        db.session.add(admin)
        
        # Создаем обычного пользователя
        user = User(
            email='user@example.com',
            first_name='Regular',
            last_name='User',
            is_admin=False,
            is_member=True,
            consent_given=True
        )
        user.set_password('userpassword')
        db.session.add(user)
        
        # Добавляем настройки
        settings = Settings(
            site_name='Brama UA e.V.',
            site_description='Українське об\'єднання в Німеччині',
            contact_email='contact@brama-ua.org',
            facebook='https://facebook.com/bramaua',
            instagram='https://instagram.com/brama_ua',
            telegram='https://t.me/brama_ua'
        )
        db.session.add(settings)
        
        # Создаем блок информации
        info_block = Block(
            title='Про нас',
            content='Brama UA - це об\'єднання українців у Німеччині, яке допомагає розвивати культурні та економічні зв\'язки.',
            type='info',
            is_active=True
        )
        db.session.add(info_block)
        
        # Создаем блок галереи
        gallery_block = Block(
            title='Галерея',
            content='Фотографії з наших заходів та проєктів.',
            type='gallery',
            is_active=True
        )
        db.session.add(gallery_block)
        db.session.commit()
        
        # Добавляем изображения в галерею
        gallery_image = GalleryImage(
            block_id=gallery_block.id,
            title='Приклад зображення',
            description='Опис зображення'
        )
        db.session.add(gallery_image)
        
        # Создаем блок проектов
        projects_block = Block(
            title='Проєкти',
            content='Наші активні та завершені проєкти.',
            type='projects',
            is_active=True
        )
        db.session.add(projects_block)
        
        # Сохраняем все в базе данных
        db.session.commit()
        
        print("База даних успішно ініціалізована з початковими даними!")
    else:
        print("База даних вже містить дані, ініціалізація не потрібна.")
