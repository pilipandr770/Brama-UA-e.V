from app import db

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(300), nullable=True)
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_mimetype = db.Column(db.String(64), nullable=True)
    description = db.Column(db.String(256), nullable=True)
    block_id = db.Column(db.Integer, db.ForeignKey('brama.blocks.id'))
    block = db.relationship('Block', backref='images') 