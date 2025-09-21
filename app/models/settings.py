from app import db
from app.models.helpers import get_table_args

class Settings(db.Model):
    __tablename__ = 'settings'
    __table_args__ = get_table_args()
    id = db.Column(db.Integer, primary_key=True)
    facebook = db.Column(db.String(256))
    instagram = db.Column(db.String(256))
    telegram = db.Column(db.String(256))
    email = db.Column(db.String(256)) 