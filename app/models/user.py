from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum

class UserRole(enum.Enum):
    member = "member"
    admin = "admin"
    founder = "founder"

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)
    # Нові поля для членів ферайну/волонтерів
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    birth_date = db.Column(db.Date)
    specialty = db.Column(db.String(128))
    join_goal = db.Column(db.String(256))
    can_help = db.Column(db.String(256))
    want_to_do = db.Column(db.String(256))
    phone = db.Column(db.String(32))
    is_member = db.Column(db.Boolean, default=True)
    consent_given = db.Column(db.Boolean, default=False)
    contributions = db.Column(db.Float, default=0.0)
    profile_photo_url = db.Column(db.String(300), nullable=True)  # URL до фото профілю
    role = db.Column(db.Enum(UserRole), default=UserRole.member)

    # Relationship with meetings
    created_meetings = db.relationship('Meeting', backref='creator', lazy='dynamic', foreign_keys='Meeting.creator_id')
    attended_meetings = db.relationship('MeetingAttendee', backref='user', lazy='dynamic')
    project_votes = db.relationship('Vote', backref='user', lazy='dynamic')
    meeting_votes = db.relationship('MeetingVote', backref='user', lazy='dynamic')
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        try:
            return check_password_hash(self.password_hash, password)
        except ValueError as e:
            if 'unsupported hash type scrypt' in str(e):
                # For users with scrypt hashed passwords, always return False
                # and let them reset their password
                # Or implement scrypt verification if needed
                return False
            raise
            
    @property
    def is_founder(self):
        return self.role == UserRole.founder
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
