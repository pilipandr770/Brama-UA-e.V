from app import db
from datetime import datetime
from app.models.helpers import get_table_args

class Vote(db.Model):
    __tablename__ = 'votes'
    __table_args__ = get_table_args()
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id' if not get_table_args() else 'brama.users.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id' if not get_table_args() else 'brama.projects.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Project(db.Model):
    __tablename__ = 'projects'
    __table_args__ = get_table_args()

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)
    goal = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.Text, nullable=False)
    implementation_plan = db.Column(db.Text, nullable=False)
    executor_info = db.Column(db.Text, nullable=False)
    total_budget = db.Column(db.Float, nullable=False)
    budget_breakdown = db.Column(db.Text, nullable=False)
    expected_result = db.Column(db.Text, nullable=False)
    risks = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(100), nullable=False)
    reporting_plan = db.Column(db.Text, nullable=False)
    
    # Додаткові поля
    category = db.Column(db.String(100))
    location = db.Column(db.String(100))
    website = db.Column(db.String(200))
    social_links = db.Column(db.Text)  # JSON рядок або список через кому
    image_url = db.Column(db.String(300), nullable=True)
    image_data = db.Column(db.LargeBinary, nullable=True)
    image_mimetype = db.Column(db.String(64), nullable=True)
    document_url = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), default='pending')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id' if not get_table_args() else 'brama.users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    votes = db.relationship('Vote', backref='project', lazy='dynamic')
    block_id = db.Column(db.Integer, db.ForeignKey('blocks.id' if not get_table_args() else 'brama.blocks.id'), nullable=True)
    block = db.relationship('Block', backref=db.backref('projects', lazy='dynamic'))

