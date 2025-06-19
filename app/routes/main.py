from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from app import db
from app.models.project import Project, Vote
from app.models.user import User
from app.models.block import Block
from app.models.gallery_image import GalleryImage
from app.models.settings import Settings
import io


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    info_block = Block.query.filter_by(type='info', is_active=True).first()
    gallery_block = Block.query.filter_by(type='gallery', is_active=True).first()
    gallery_images = GalleryImage.query.filter_by(block_id=gallery_block.id).all() if gallery_block else []
    projects_block = Block.query.filter_by(type='projects', is_active=True).first()
    projects = Project.query.filter_by(status='approved').order_by(Project.created_at.desc()).all()
    settings = Settings.query.first()
    return render_template('index.html', info_block=info_block, gallery_block=gallery_block, gallery_images=gallery_images, projects_block=projects_block, projects=projects, settings=settings)

@main_bp.route('/submit-project', methods=['GET', 'POST'])
def submit_project():
    if request.method == 'POST':
        try:
            image_file = request.files.get('image_file')
            image_data = image_file.read() if image_file and image_file.filename else None
            image_mimetype = image_file.mimetype if image_file and image_file.filename else None
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
                document_url=request.form.get('document_url'),
                user_id=1,  # тимчасово хардкод, поки немає логіну
                image_data=image_data,
                image_mimetype=image_mimetype,
                status='pending'
            )
            db.session.add(project)
            db.session.commit()
            flash("Проєкт успішно подано! Очікує модерації.", "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            flash(f"Помилка при збереженні: {e}", "danger")

    return render_template('submit_project.html')

@main_bp.route('/project/image/<int:project_id>')
def project_image_file(project_id):
    project = Project.query.get_or_404(project_id)
    if project.image_data:
        return send_file(io.BytesIO(project.image_data), mimetype=project.image_mimetype)
    elif project.image_url:
        return redirect(project.image_url)
    else:
        return '', 404

from flask import session

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            flash("Користувач з такою поштою вже існує.", "danger")
            return redirect(url_for('main.register'))
        user = User(
            email=email,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            birth_date=request.form.get('birth_date'),
            specialty=request.form.get('specialty'),
            join_goal=request.form.get('join_goal'),
            can_help=request.form.get('can_help'),
            want_to_do=request.form.get('want_to_do'),
            phone=request.form.get('phone'),
            is_member=True,
            consent_given=bool(request.form.get('consent_given')),
            contributions=0.0
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        flash("Реєстрація успішна! Ви стали членом ферайну.", "success")
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
    from sqlalchemy import func
    total_contributions = db.session.query(func.sum(User.contributions)).scalar() or 0.0
    last_contributor = User.query.filter(User.contributions > 0).order_by(User.contributions.desc()).first()
    return render_template('dashboard.html', user=user, total_contributions=total_contributions, last_contributor=last_contributor)

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/impressum')
def impressum():
    return render_template('impressum.html')

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/vote/<int:project_id>', methods=['POST'])
def vote(project_id):
    user_id = session.get('user_id')
    if not user_id:
        flash('Треба увійти, щоб голосувати.', 'warning')
        return redirect(url_for('main.login'))
    project = Project.query.get_or_404(project_id)
    existing_vote = Vote.query.filter_by(user_id=user_id, project_id=project_id).first()
    if existing_vote:
        flash('Ви вже підтримали цей проєкт!', 'info')
        return redirect(url_for('main.index'))
    vote = Vote(user_id=user_id, project_id=project_id)
    db.session.add(vote)
    db.session.commit()
    flash('Ваш голос зараховано!', 'success')
    return redirect(url_for('main.index'))
