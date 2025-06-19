from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
