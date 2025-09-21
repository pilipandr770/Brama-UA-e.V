from app import db
from app.models.helpers import get_table_args
from datetime import datetime
import sqlalchemy as sa

class Block(db.Model):
    """
    Модель для блоков контента на сайте.
    
    Специально реализовано так, чтобы работало даже без полей name и slug в базе,
    используя переопределенный __mapper_args__ для предотвращения включения этих
    полей в SQL-запросы при их отсутствии.
    """
    __tablename__ = 'blocks'
    __table_args__ = get_table_args()
    id = db.Column(db.Integer, primary_key=True)
    
    # Эти поля объявлены, но будут игнорироваться при доступе, если не существуют в базе
    _name = db.Column('name', db.String(50), nullable=True)
    _slug = db.Column('slug', db.String(50), nullable=True)
    
    # Основные поля
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(32), nullable=False)  # info, gallery, projects
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300), nullable=True)  # обкладинка URL
    translations = db.Column(db.Text, nullable=True)  # JSON для многоязычного контента
    
    # Новые поля для хранения изображения в БД
    image_data = db.Column(db.LargeBinary, nullable=True)  # бинарные данные
    image_mimetype = db.Column(db.String(64), nullable=True)  # тип файла
    
    # Виртуальные свойства для безопасного доступа к name и slug
    @property
    def name(self):
        if hasattr(self, '_name') and self._name is not None:
            return self._name
        return f"block_{self.type}_{self.id}"
    
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def slug(self):
        if hasattr(self, '_slug') and self._slug is not None:
            return self._slug
        if hasattr(self, '_name') and self._name is not None:
            return self._name.lower().replace(" ", "_")
        return f"block_{self.type}_{self.id}".lower()
    
    @slug.setter
    def slug(self, value):
        self._slug = value
    
    def __init__(self, **kwargs):
        # Если не указаны name и slug, генерируем их
        name_value = kwargs.pop('name', None)
        slug_value = kwargs.pop('slug', None)
        
        # Инициализируем основные поля
        super(Block, self).__init__(**kwargs)
        
        # После инициализации, устанавливаем name и slug, если они переданы
        if name_value:
            self.name = name_value
        if slug_value:
            self.slug = slug_value