from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum

class UserRole(enum.Enum):
    member = "member"
    admin = "admin"
    founder = "founder"

from app.models.helpers import get_table_args

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    __table_args__ = get_table_args()

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    role = db.Column(db.String(50), default='member')
    is_blocked = db.Column(db.Boolean, default=False)

    # Relationship with meetings
    created_meetings = db.relationship('Meeting', backref='creator', lazy='dynamic', foreign_keys='Meeting.creator_id')
    attended_meetings = db.relationship('MeetingAttendee', backref='user', lazy='dynamic', 
                                      primaryjoin="User.id==MeetingAttendee.user_id")
    # project_votes relationship commented out because Vote model doesn't exist (brama.votes table missing)
    # project_votes = db.relationship('Vote', backref='user', lazy='dynamic')
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
    def is_admin(self):
        """Check if user has admin role"""
        try:
            return (self.role == 'admin') or (isinstance(self.role, UserRole) and self.role == UserRole.admin)
        except Exception:
            return False
    
    @property
    def is_founder(self):
        # role stored as string; support old enum-based comparisons gracefully
        try:
            return (self.role == 'founder') or (isinstance(self.role, UserRole) and self.role == UserRole.founder)
        except Exception:
            return False
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
