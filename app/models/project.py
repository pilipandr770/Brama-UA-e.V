from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

main_bp = Blueprint('main', __name__)

class Project(db.Model):
    __tablename__ = 'projects'

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
    image_url = db.Column(db.String(300))
    document_url = db.Column(db.String(300))

    status = db.Column(db.String(20), default='draft')
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@main_bp.route('/')
def index():
    # Отримаємо всі проекти для головної сторінки (поки що всі)
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('index.html', projects=projects)

@main_bp.route('/submit-project', methods=['GET', 'POST'])
def submit_project():
    if request.method == 'POST':
        try:
            project = Project(
                title=request.form['title'],
                problem_description=request.form['problem_description'],
                goal=request.form['goal'],
                target_audience=request.form['target_audience'],
                implementation_plan=request.form['implementation_plan'],
                executor_info=request.form['executor_info'],
                total_budget=request.form['total_budget'],
                budget_breakdown=request.form['budget_breakdown'],
                expected_result=request.form['expected_result'],
                risks=request.form['risks'],
                duration=request.form['duration'],
                reporting_plan=request.form['reporting_plan'],
                category=request.form.get('category'),
                location=request.form.get('location'),
                website=request.form.get('website'),
                social_links=request.form.get('social_links'),
                image_url=request.form.get('image_url'),
                document_url=request.form.get('document_url'),
                user_id=1  # тимчасово хардкод, поки немає логіну
            )
            db.session.add(project)
            db.session.commit()
            flash("Проєкт успішно подано!", "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f"Помилка при збереженні: {e}", "danger")

    return render_template('submit_project.html')
