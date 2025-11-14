from app import db
from app.models.helpers import get_table_args
from datetime import datetime

class Block(db.Model):
    """
    Model for content blocks on the website.
    Simplified to match actual database structure after database recovery.
    """
    __tablename__ = 'blocks'
    __table_args__ = get_table_args()
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(32), nullable=False)  # info, gallery, projects
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300), nullable=True)
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_mimetype = db.Column(db.String(64), nullable=True)
    
    def __repr__(self):
        return f'<Block {self.id}: {self.title}>'
