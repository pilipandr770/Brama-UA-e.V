from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, current_app, session
from flask_babel import gettext as _
from app import db
from app.models.project import Project, Vote
from app.models.user import User
from app.models.block import Block
from app.models.gallery_image import GalleryImage
from app.models.settings import Settings
from app.forms import EditProfileForm, LoginForm, RegistrationForm
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.utils import secure_filename
from app.cache import cache, get_active_blocks, get_gallery_images, get_approved_projects, get_settings
import io
import os
from datetime import datetime


main_bp = Blueprint('main', __name__)

from app.models.helpers import get_translated_content

def get_language_specific_template(base_name):
    """Helper function to get language-specific template"""
    language = session.get('language', 'de')  # Default to German

    if language == 'en':
        return f"{base_name}_en.html"
    else:
        return f"{base_name}.html"

@main_bp.route('/')
@cache.cached(timeout=300)  # Кэширование главной страницы на 5 минут
def index():
    # Используем кэшированные функции для оптимизации
    all_active_blocks = get_active_blocks()

    # Разделяем блоки по типам для обратной совместимости с шаблоном
    info_block = next((block for block in all_active_blocks if block.type == 'info'), None)
    gallery_block = next((block for block in all_active_blocks if block.type == 'gallery'), None)
    projects_block = next((block for block in all_active_blocks if block.type == 'projects'), None)

    # Получаем дополнительные блоки (все кроме стандартных типов)
    additional_blocks = [block for block in all_active_blocks
                        if block.type not in ['info', 'gallery', 'projects']]

    # Получаем изображения галереи только если есть блок галереи
    gallery_images = []
    if gallery_block:
        gallery_images = get_gallery_images(gallery_block.id)

    # Получаем проекты только если есть блок проектов
    projects = []
    if projects_block:
        try:
            projects = get_approved_projects(projects_block.id)
        except Exception as e:
            # Временный обходной путь для проблемы PostgreSQL VARCHAR type 1043
            current_app.logger.error(f"Error loading projects: {e}")
            projects = []

    # Получаем настройки
    settings = get_settings()

    # Process translations for blocks (оптимизировано - только для видимых блоков)
    blocks_to_translate = [b for b in [info_block, gallery_block, projects_block] + additional_blocks if b]

    for block in blocks_to_translate:
        block.translated_title = get_translated_content(block, 'title')
        block.translated_content = get_translated_content(block, 'content')

    return render_template(
        'index.html',
        info_block=info_block,
        gallery_block=gallery_block,
        gallery_images=gallery_images,
        projects_block=projects_block,
        projects=projects,
        additional_blocks=additional_blocks,
        settings=settings
    )

@main_bp.route('/submit-project', methods=['GET', 'POST'])
@login_required
def submit_project():
    if request.method == 'POST':
        try:
            image_file = request.files.get('image_file')
            # Встановлюємо block_id для активного блоку проектів
            projects_block = Block.query.filter_by(type='projects', is_active=True).first()
            block_id = projects_block.id if projects_block else None
            
            # Base project data without optional fields
            project_data = {
                'title': request.form['title'],
                'problem_description': request.form['problem_description'],
                'goal': request.form['goal'],
                'target_audience': request.form['target_audience'],
                'implementation_plan': request.form['implementation_plan'],
                'executor_info': request.form['executor_info'],
                'total_budget': request.form['total_budget'],
                'budget_breakdown': request.form['budget_breakdown'],
                'expected_result': request.form['expected_result'],
                'risks': request.form['risks'],
                'duration': request.form['duration'],
                'reporting_plan': request.form['reporting_plan'],
                'category': request.form.get('category'),
                'location': request.form.get('location'),
                'website': request.form.get('website'),
                'social_links': request.form.get('social_links'),
                'user_id': current_user.id if current_user.is_authenticated else None,
                'status': 'pending',
                'block_id': block_id
            }
            
            # Only add optional fields if they exist in database
            if Project._existing_columns:
                if 'image_data' in Project._existing_columns and image_file and image_file.filename:
                    project_data['image_data'] = image_file.read()
                if 'image_mimetype' in Project._existing_columns and image_file and image_file.filename:
                    project_data['image_mimetype'] = image_file.mimetype
                if 'document_url' in Project._existing_columns:
                    project_data['document_url'] = request.form.get('document_url')
            
            project = Project(**project_data)
            db.session.add(project)
            db.session.commit()
            flash(_("Проєкт успішно подано! Очікує модерації."), "success")
            return redirect(url_for('main.index'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Project submission error: {type(e).__name__}: {str(e)}")
            # Use simple string concatenation to avoid Flask-Babel format issues
            error_msg = _("Помилка при збереженні") + f": {str(e)}"
            flash(error_msg, "danger")

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

@main_bp.route('/gallery/image/<int:image_id>')
@cache.cached(timeout=86400)  # Кэш на 24 часа для изображений галереи
def gallery_image_file(image_id):
    try:
        img = GalleryImage.query.get_or_404(image_id)
        if img.image_data:
            response = send_file(
                io.BytesIO(img.image_data), 
                mimetype=img.image_mimetype
            )
            # Устанавливаем заголовок кэширования вручную с длительным сроком
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            # Добавляем ETag для проверки изменений
            response.add_etag()
            return response
        elif img.image_url:
            return redirect(img.image_url)
        else:
            print(f"Error: Gallery image {image_id} has no data or URL")
            return '', 404
    except Exception as e:
        print(f"Error serving gallery image {image_id}: {str(e)}")
        return '', 500

# Block image route removed - images are now served from filesystem

from flask import session

@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash(_("Користувач з такою поштою вже існує."), "danger")
            return redirect(url_for('main.register'))
        
        user = User(
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        # Автоматическая авторизация
        login_user(user)
        session['user_id'] = user.id  # Сохраняем для обратной совместимости
        
        flash(_("Реєстрація успішна! Ви стали членом ферайну."), "success")
        return redirect(url_for('main.dashboard'))
    
    return render_template('register.html', form=form)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            # Используем remember=True если пользователь выбрал "запомнить меня"
            login_user(user, remember=form.remember.data)
            session['user_id'] = user.id  # Сохраняем для обратной совместимости
            flash(_("Ви увійшли!"), "success")
            
            # Перенаправление на страницу, которую пользователь запрашивал до входа
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                if user.is_admin:
                    next_page = url_for('admin.dashboard')
                elif user.is_founder:
                    next_page = url_for('founder.dashboard')
                else:
                    next_page = url_for('main.dashboard')
            return redirect(next_page)
        flash(_("Невірний email або пароль"), "danger")
    return render_template('login.html', form=form)


@main_bp.route('/logout')
def logout():
    logout_user()
    session.pop('user_id', None)  # Удаляем для обратной совместимости
    flash(_("Ви вийшли з акаунту."), "info")
    return redirect(url_for('main.index'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Получаем баланс ферайна из настроек
    from app.models.settings import Settings
    settings = Settings.query.first()
    
    # Contributions field removed from User model
    last_contributor = None
    
    # Используем баланс из настроек, если он установлен, иначе считаем сумму взносов
    if settings and hasattr(settings, 'association_balance') and settings.association_balance is not None:
        total_contributions = float(settings.association_balance)
    else:
        total_contributions = 0.0
    
    return render_template('dashboard.html', total_contributions=total_contributions, last_contributor=last_contributor)

@main_bp.route('/privacy')
def privacy():
    return render_template(get_language_specific_template('privacy'))

@main_bp.route('/impressum')
def impressum():
    return render_template(get_language_specific_template('impressum'))

@main_bp.route('/agb')
def agb():
    return render_template(get_language_specific_template('agb'))

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/vote/<int:project_id>', methods=['POST'])
@login_required
def vote(project_id):
    project = Project.query.get_or_404(project_id)
    existing_vote = Vote.query.filter_by(user_id=current_user.id, project_id=project_id).first()
    
    if existing_vote:
        flash(_('Ви вже підтримали цей проєкт!'), 'info')
        return redirect(url_for('main.index'))
        
    vote = Vote(user_id=current_user.id, project_id=project_id)
    db.session.add(vote)
    db.session.commit()
    
    flash(_('Ваш голос зараховано!'), 'success')
    return redirect(url_for('main.index'))

@main_bp.route('/upload-profile-photo', methods=['POST'])
@login_required
def upload_profile_photo():
    if 'profile_photo' not in request.files:
        flash(_("Файл не вибрано"), "warning")
        return redirect(url_for('main.dashboard'))
    
    profile_photo = request.files['profile_photo']
    
    if profile_photo.filename == '':
        flash(_("Файл не вибрано"), "warning")
        return redirect(url_for('main.dashboard'))
    
    if profile_photo:
        # Генерируем уникальное имя файла
        import os
        from werkzeug.utils import secure_filename
        from datetime import datetime
        
        # Создаем директорию для загрузок, если она не существует
        upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads', 'profiles')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Создаем уникальное имя файла
        filename = secure_filename(profile_photo.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{current_user.id}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Сохраняем файл
        profile_photo.save(file_path)
        
        # Устанавливаем URL для сохранения в БД
        current_user.profile_photo_url = url_for('static', filename=f'uploads/profiles/{unique_filename}')
        db.session.commit()
        
        flash(_("Фото профілю оновлено"), "success")
    
    return redirect(url_for('main.dashboard'))


@main_bp.route('/profile')
@login_required
def profile():
    """Страница профиля пользователя"""
    return render_template('profile.html')


@main_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Редактирование профиля пользователя"""
    form = EditProfileForm()
    
    if request.method == 'GET':
        # Заполняем форму текущими данными пользователя
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        # Removed fields that no longer exist in User model
        # form.birth_date.data = current_user.birth_date
        # form.specialty.data = current_user.specialty
        # form.join_goal.data = current_user.join_goal
        # form.can_help.data = current_user.can_help
        # form.want_to_do.data = current_user.want_to_do
        form.phone.data = current_user.phone if hasattr(current_user, 'phone') else ''
    
    if form.validate_on_submit():
        # Обновляем данные пользователя
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        # Removed fields that no longer exist in User model
        # current_user.birth_date = form.birth_date.data
        # current_user.specialty = form.specialty.data
        # current_user.join_goal = form.join_goal.data
        # current_user.can_help = form.can_help.data
        # current_user.want_to_do = form.want_to_do.data
        if hasattr(current_user, 'phone'):
            current_user.phone = form.phone.data
        
        # Обработка загрузки фото профиля
        if form.profile_photo.data:
            profile_photo = form.profile_photo.data
            
            # Создаем директорию для загрузки, если она не существует
            upload_dir = os.path.join(current_app.static_folder, 'uploads/profiles')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Создаем уникальное имя файла
            filename = secure_filename(profile_photo.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{timestamp}_{current_user.id}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Сохраняем файл
            profile_photo.save(file_path)
            
            # Устанавливаем URL для сохранения в БД
            current_user.profile_photo_url = url_for('static', filename=f'uploads/profiles/{unique_filename}')
        
        db.session.commit()
        flash(_('Профіль успішно оновлено'), 'success')
        return redirect(url_for('main.profile'))
    
    return render_template('edit_profile.html', form=form)
