from app import db

class GalleryImage(db.Model):
    __tablename__ = 'gallery_images'
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(300), nullable=False)
    description = db.Column(db.String(256), nullable=True)
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id'))
    block = db.relationship('Block', backref='images') 