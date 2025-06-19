from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.project import Project
from app.models.user import User
from app.models.block import Block
from app.models.gallery_image import GalleryImage


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    info_block = Block.query.filter_by(type='info', is_active=True).first()
    gallery_block = Block.query.filter_by(type='gallery', is_active=True).first()
    gallery_images = GalleryImage.query.filter_by(block_id=gallery_block.id).all() if gallery_block else []
    projects_block = Block.query.filter_by(type='projects', is_active=True).first()
    projects = Project.query.order_by(Project.created_at.desc()).all()
    return render_template('index.html', info_block=info_block, gallery_block=gallery_block, gallery_images=gallery_images, projects_block=projects_block, projects=projects)

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

from flask import session

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Користувач з такою поштою вже існує.", "danger")
            return redirect(url_for('main.register'))
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        flash("Реєстрація успішна!", "success")
        return redirect(url_for('main.dashboard'))
    return render_template('register.html')


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            flash("Ви увійшли!", "success")
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('main.dashboard'))
        flash("Невірний email або пароль", "danger")
    return render_template('login.html')


@main_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Ви вийшли з акаунту.", "info")
    return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        flash("Увійдіть, щоб побачити кабінет", "warning")
        return redirect(url_for('main.login'))
    
    user = User.query.get(user_id)
    return render_template('dashboard.html', user=user)

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/impressum')
def impressum():
    return render_template('impressum.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')
