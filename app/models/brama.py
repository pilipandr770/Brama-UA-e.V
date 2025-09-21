from app import db
from datetime import datetime
from app.models.helpers import get_table_args

class Brama(db.Model):
    __tablename__ = 'brama'
    __table_args__ = get_table_args()
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Brama {self.title}>'
