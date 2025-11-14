from app import db
from app.models.helpers import get_table_args

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    __table_args__ = get_table_args()
    id = db.Column(db.Integer, primary_key=True)
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_mimetype = db.Column(db.String(64), nullable=True)
    description = db.Column(db.String(256), nullable=True)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id' if not get_table_args() else 'brama.blocks.id'))
    block = db.relationship('Block', backref=db.backref('images', lazy='dynamic'))