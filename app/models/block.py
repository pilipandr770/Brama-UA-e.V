from app import db
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime

class Block(db.Model):
    __tablename__ = 'blocks'
    __table_args__ = {'schema': 'brama'}
    id = db.Column(db.Integer, primary_key=True)
    
    # Оставляем поля для совместимости с существующими данными
    # и делаем их не строго обязательными, чтобы приложение запустилось
    name = db.Column(db.String(50), nullable=True, default="legacy")
    slug = db.Column(db.String(50), nullable=True)
    
    # Current fields
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(32), nullable=False)  # info, gallery, projects
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300), nullable=True)  # обкладинка URL
    # Новые поля для хранения изображения напрямую в БД
    image_data = db.Column(db.LargeBinary, nullable=True)  # бинарные данные
    image_mimetype = db.Column(db.String(64), nullable=True)  # тип файла
    translations = db.Column(db.Text, nullable=True)  # JSON для многоязычного контента
    
    def __init__(self, **kwargs):
        # Автоматически заполняем name и slug, если они не указаны
        if 'name' not in kwargs or not kwargs['name']:
            kwargs['name'] = f"block_{kwargs.get('type', 'unknown')}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if 'slug' not in kwargs or not kwargs['slug']:
            kwargs['slug'] = kwargs['name'].lower().replace(" ", "_")
            
        super(Block, self).__init__(**kwargs)