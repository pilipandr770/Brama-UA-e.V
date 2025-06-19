from app import db

class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True)
    facebook = db.Column(db.String(256))
    instagram = db.Column(db.String(256))
    telegram = db.Column(db.String(256))
    email = db.Column(db.String(256)) 