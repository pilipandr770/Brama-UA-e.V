from app import db
from sqlalchemy.dialects.postgresql import JSON

class Block(db.Model):
    __tablename__ = 'blocks'
    __table_args__ = {'schema': 'brama'}
    id = db.Column(db.Integer, primary_key=True)
    # Deprecated/legacy fields (kept for compatibility)
    name = db.Column(db.String(50), nullable=False, default="legacy")
    slug = db.Column(db.String(50), unique=True, nullable=True)
    
    # Current fields
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(32), nullable=False)  # info, gallery, projects
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300), nullable=True)  # обкладинка URL
    # Новые поля для хранения изображения напрямую в БД
    image_data = db.Column(db.LargeBinary, nullable=True)  # бинарные данные
    image_mimetype = db.Column(db.String(64), nullable=True)  # тип файла
    translations = db.Column(JSON, nullable=True)  # JSON для многоязычного контента