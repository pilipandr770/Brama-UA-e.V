from app import db
from app.models.helpers import get_table_args

class Report(db.Model):
    __tablename__ = 'reports'
    __table_args__ = get_table_args()
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now()) 