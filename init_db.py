from app import create_app, db
from app.models.user import User
from app.models.block import Block
from app.models.gallery_image import GalleryImage
from app.models.settings import Settings

app = create_app()

with app.app_context():
    # Создаем все таблицы
    db.create_all()
    
    # Проверяем, есть ли уже записи в таблицах
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
        
        # Создаем настройки по умолчанию
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
