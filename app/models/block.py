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
    
    # Определяем name и slug как отложенные загружаемые колонки, чтобы избежать ошибок
    # при отсутствии их в базе данных. Они будут загружены только при явном доступе.
    _name = db.deferred(db.Column('name', db.String(50), nullable=True))
    _slug = db.deferred(db.Column('slug', db.String(50), nullable=True))
    
    # Устанавливаем mapper_args для предотвращения проблем в случае отсутствия колонок
    @classmethod
    def __declare_last__(cls):
        """
        Hook called after mapper configuration is complete
        We use it to exclude columns that might not exist in the DB
        """
        from sqlalchemy import inspect
        
        # Try to detect if columns exist in the database
        try:
            engine = db.engine
            insp = inspect(engine)
            
            # Try to get columns for different schema scenarios
            existing_columns = set()
            schemas_to_check = ['brama', None]  # None = без схемы (как в SQLite)
            
            for schema in schemas_to_check:
                try:
                    cols = insp.get_columns(cls.__tablename__, schema=schema)
                    existing_columns = {col['name'] for col in cols}
                    break  # Found table, exit loop
                except Exception:
                    continue
            
            # Exclude properties if columns don't exist
            exclude_props = []
            if 'name' not in existing_columns:
                exclude_props.append('_name')
            if 'slug' not in existing_columns:
                exclude_props.append('_slug')
            if 'image_data' not in existing_columns:
                exclude_props.append('image_data')
            if 'image_mimetype' not in existing_columns:
                exclude_props.append('image_mimetype')
                
            # Apply exclude_properties only if needed
            if exclude_props:
                # Get current mapper
                mapper = inspect(cls).mapper
                # Update exclude_properties in __mapper_args__
                if hasattr(mapper, 'exclude_properties'):
                    mapper.exclude_properties = list(set(mapper.exclude_properties) | set(exclude_props))
                else:
                    mapper._exclude_properties = exclude_props
        except Exception as e:
            import logging
            logging.getLogger('app.models.block').warning(f"Error in __declare_last__: {e}")
            # If any error occurs, just continue without updating mapper
            pass
    
    # Основные поля
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(32), nullable=False)  # info, gallery, projects
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300), nullable=True)  # обкладинка URL
    translations = db.Column(db.Text, nullable=True)  # JSON для многоязычного контента
    
    # Новые поля для хранения изображения в БД - используем deferred для безопасного доступа
    # если колонки отсутствуют в БД
    image_data = db.deferred(db.Column(db.LargeBinary, nullable=True))  # бинарные данные
    image_mimetype = db.deferred(db.Column(db.String(64), nullable=True))  # тип файла
    
    # Виртуальные свойства для безопасного доступа к name и slug
    @property
    def name(self):
        try:
            if hasattr(self, '_name') and self._name is not None:
                return self._name
        except (sa.exc.SQLAlchemyError, AttributeError):
            pass
        return f"block_{self.type}_{self.id}"
    
    @name.setter
    def name(self, value):
        try:
            self._name = value
        except (sa.exc.SQLAlchemyError, AttributeError):
            pass  # Silently ignore if column doesn't exist
    
    @property
    def slug(self):
        try:
            if hasattr(self, '_slug') and self._slug is not None:
                return self._slug
            if hasattr(self, '_name') and self._name is not None:
                return self._name.lower().replace(" ", "_")
        except (sa.exc.SQLAlchemyError, AttributeError):
            pass
        return f"block_{self.type}_{self.id}".lower()
    
    @slug.setter
    def slug(self, value):
        try:
            self._slug = value
        except (sa.exc.SQLAlchemyError, AttributeError):
            pass  # Silently ignore if column doesn't exist
    
    def __init__(self, **kwargs):
        # Если не указаны name и slug, генерируем их
        name_value = kwargs.pop('name', None)
        slug_value = kwargs.pop('slug', None)
        
        # Remove these keys if they exist in kwargs to prevent errors
        kwargs.pop('_name', None)
        kwargs.pop('_slug', None)
        
        # Инициализируем основные поля
        super(Block, self).__init__(**kwargs)
        
        # После инициализации, устанавливаем name и slug, если они переданы
        try:
            if name_value:
                self.name = name_value
            if slug_value:
                self.slug = slug_value
        except (sa.exc.SQLAlchemyError, AttributeError):
            # Silently ignore if columns don't exist in the DB
            pass