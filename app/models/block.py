from app import db

class Block(db.Model):
    __tablename__ = 'blocks'
    __table_args__ = {'schema': 'brama'}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(32), nullable=False)  # info, gallery, projects
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300), nullable=True)  # обкладинка
    translations = db.Column(db.Text, nullable=True)  # JSON string for multilingual content