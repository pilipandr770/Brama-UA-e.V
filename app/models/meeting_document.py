"""
Model for meeting documents
"""
from app import db
from datetime import datetime

class MeetingDocument(db.Model):
    __tablename__ = 'meeting_documents'
    __table_args__ = {'schema': 'brama'}

    id = db.Column(db.Integer, primary_key=True)
    meeting_id = db.Column(db.Integer, db.ForeignKey('brama.meetings.id'))
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_data = db.Column(db.LargeBinary, nullable=False)  # Binary data of the file
    file_mimetype = db.Column(db.String(128), nullable=False)  # MIME type of the file
    file_size = db.Column(db.Integer, nullable=False)  # Size of file in bytes
    uploaded_by = db.Column(db.Integer, db.ForeignKey('brama.users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_public = db.Column(db.Boolean, default=False)  # If False, only founders can see it

    # Define relationships
    meeting = db.relationship('Meeting', backref=db.backref('documents', lazy='dynamic', cascade='all, delete-orphan'))
    uploader = db.relationship('User', backref=db.backref('uploaded_documents', lazy='dynamic'))
