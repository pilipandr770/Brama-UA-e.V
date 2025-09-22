from flask import Blueprint, render_template, redirect, url_for, session, flash, request, send_file
from app import db
from app.models.user import User, UserRole
from app.models.block import Block
from app.models.gallery_image import GalleryImage
from app.models.project import Project
from app.models.settings import Settings
from app.models.report import Report
from app.cache import cache
from functools import wraps
import io

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        user = User.query.get(user_id) if user_id else None
        if not user or not user.is_admin:
            flash('Доступ лише для адміністратора!', 'danger')
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@admin_required
def dashboard():
    users = User.query.all()
    blocks = Block.query.all()
    gallery = GalleryImage.query.all()
    projects = Project.query.all()
    settings = Settings.query.first()
    reports = Report.query.order_by(Report.created_at.desc()).all()
    return render_template('admin/dashboard.html', users=users, blocks=blocks, gallery=gallery, projects=projects, settings=settings, reports=reports)

@admin_bp.route('/toggle-block-user/<int:user_id>')
@admin_required
def toggle_block_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Не можна блокувати адміністратора!', 'danger')
        return redirect(url_for('admin.dashboard'))
    user.is_blocked = not user.is_blocked
    db.session.commit()
    flash(f'Користувач {user.email} ' + ('заблокований.' if user.is_blocked else 'розблокований.'), 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/block/create', methods=['GET', 'POST'])
@admin_required
def create_block():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        type_ = request.form['type']
        image_url = request.form.get('image_url')
        
        # Обработка загруженного файла
        image_file = request.files.get('image_file')
        image_data = None
        image_mimetype = None
        
        if image_file and image_file.filename:
            # Читаем файл целиком в память для сохранения в базе данных
            image_data = image_file.read()
            image_mimetype = image_file.mimetype
            
            # Можем опционально сохранить и URL, если нужна совместимость
            try:
                # Генерируем уникальное имя файла
                import os
                from werkzeug.utils import secure_filename
                from datetime import datetime
                
                # Создаем директорию для загрузок, если она не существует
                upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                # Создаем уникальное имя файла
                filename = secure_filename(image_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(upload_dir, unique_filename)
                
                # Сохраняем файл и с диска тоже (для совместимости)
                with open(file_path, 'wb') as f:
                    f.write(image_data)
                
                # Устанавливаем URL для сохранения в БД
                image_url = url_for('static', filename=f'uploads/{unique_filename}')
            except Exception as e:
                # В случае ошибки сохранения файла на диск,
                # продолжаем работу, так как изображение уже есть в памяти
                print(f"Warning: Could not save image to disk: {e}")
        
        from datetime import datetime
        # Генерируем уникальное имя и slug
        block_name = f"block_{type_}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        block_slug = block_name.lower().replace(" ", "_")
        
        block = Block(
            name=block_name,
            slug=block_slug,
            title=title, 
            content=content, 
            type=type_, 
            image_url=image_url,
            image_data=image_data,
            image_mimetype=image_mimetype
        )
        db.session.add(block)
        db.session.commit()
        flash('Блок створено!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_block.html', block=None)

@admin_bp.route('/block/edit/<int:block_id>', methods=['GET', 'POST'])
@admin_required
def edit_block(block_id):
    block = Block.query.get_or_404(block_id)
    if request.method == 'POST':
        block.title = request.form['title']
        block.content = request.form['content']
        block.type = request.form['type']
        
        # Сначала проверяем загруженный файл
        image_file = request.files.get('image_file')
        if image_file and image_file.filename:
            # Читаем файл целиком в память для сохранения в базе данных
            image_data = image_file.read()
            block.image_data = image_data
            block.image_mimetype = image_file.mimetype
            
            # Также сохраняем на диск для совместимости
            try:
                # Генерируем уникальное имя файла
                import os
                from werkzeug.utils import secure_filename
                from datetime import datetime
                
                # Создаем директорию для загрузок, если она не существует
                upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
                if not os.path.exists(upload_dir):
                    os.makedirs(upload_dir)
                
                # Создаем уникальное имя файла
                filename = secure_filename(image_file.filename)
                timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                unique_filename = f"{timestamp}_{filename}"
                file_path = os.path.join(upload_dir, unique_filename)
                
                # Сохраняем файл
                with open(file_path, 'wb') as f:
                    f.write(image_data)
                
                # Устанавливаем URL для сохранения в БД (для совместимости)
                block.image_url = url_for('static', filename=f'uploads/{unique_filename}')
            except Exception as e:
                # В случае ошибки сохранения файла на диск,
                # продолжаем работу, так как изображение уже есть в памяти
                print(f"Warning: Could not save image to disk: {e}")
        elif request.form.get('remove_image') == '1':
            # Если пользователь хочет удалить изображение
            block.image_url = None
            block.image_data = None
            block.image_mimetype = None
            flash('Зображення видалено!', 'success')
        else:
            # Если файл не загружен, используем URL из формы
            url = request.form.get('image_url')
            if url != block.image_url:  # Если URL изменился
                block.image_url = url
                # Если URL изменился и изображение сохранено в БД, очистим его
                if block.image_data:
                    block.image_data = None
                    block.image_mimetype = None
                
        db.session.commit()
        flash('Блок оновлено!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_block.html', block=block)

@admin_bp.route('/block/delete/<int:block_id>', methods=['POST'])
@admin_required
def delete_block(block_id):
    block = Block.query.get_or_404(block_id)
    db.session.delete(block)
    db.session.commit()
    flash('Блок видалено!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/gallery/add', methods=['GET', 'POST'])
@admin_required
def add_gallery_image():
    if request.method == 'POST':
        try:
            block_id = request.form.get('block_id')
            descriptions = request.form.getlist('description')
            files = request.files.getlist('images')
            
            if not files or not any(file.filename for file in files):
                flash('Будь ласка, виберіть хоча б одне зображення', 'error')
                blocks = Block.query.filter_by(type='gallery').all()
                return render_template('admin/add_gallery_image.html', blocks=blocks)
            
            added_images = 0
            for idx, file in enumerate(files):
                if file and file.filename:
                    # Читаем файл целиком в память
                    file_data = file.read()
                    if not file_data:
                        continue
                    
                    # Создаем запись в базе данных
                    img = GalleryImage(
                        image_data=file_data,
                        image_mimetype=file.mimetype,
                        description=descriptions[idx] if idx < len(descriptions) else '',
                        block_id=block_id
                    )
                    db.session.add(img)
                    added_images += 1
            
            # Коммитим все изменения в базе данных
            db.session.commit()
            
            flash(f'Додано {added_images} фото до галереї!', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Помилка при додаванні фото: {str(e)}', 'error')
            print(f"Error adding gallery images: {str(e)}")
            
    blocks = Block.query.filter_by(type='gallery').all()
    return render_template('admin/add_gallery_image.html', blocks=blocks)

@admin_bp.route('/gallery/image/<int:image_id>')
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

@admin_bp.route('/gallery/delete/<int:image_id>', methods=['POST'])
@admin_required
def delete_gallery_image(image_id):
    img = GalleryImage.query.get_or_404(image_id)
    db.session.delete(img)
    db.session.commit()
    flash('Фото видалено з галереї!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/approve_project/<int:project_id>', methods=['POST'])
@admin_required
def approve_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = 'approved'
    db.session.commit()
    flash('Проєкт підтверджено!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/reject_project/<int:project_id>', methods=['POST'])
@admin_required
def reject_project(project_id):
    project = Project.query.get_or_404(project_id)
    project.status = 'rejected'
    db.session.commit()
    flash('Проєкт відхилено.', 'info')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/settings/social', methods=['GET', 'POST'])
@admin_required
def edit_social_settings():
    settings = Settings.query.first()
    if not settings:
        settings = Settings()
        db.session.add(settings)
        db.session.commit()
    if request.method == 'POST':
        settings.facebook = request.form.get('facebook')
        settings.instagram = request.form.get('instagram')
        settings.telegram = request.form.get('telegram')
        settings.email = request.form.get('email')
        db.session.commit()
        flash('Соцмережі оновлено!', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/edit_social.html', settings=settings)

@admin_bp.route('/update_contribution/<int:user_id>', methods=['POST'])
@admin_required
def update_contribution(user_id):
    user = User.query.get_or_404(user_id)
    try:
        new_contribution = float(request.form.get('contribution', 0))
        user.contributions = new_contribution
        db.session.commit()
        flash(f'Внесок для {user.first_name} {user.last_name} оновлено!', 'success')
    except Exception as e:
        flash(f'Помилка при оновленні внеску: {e}', 'danger')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/edit_project/<int:project_id>', methods=['GET', 'POST'])
@admin_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    
    if request.method == 'POST':
        # Обновляем данные проекта
        project.title = request.form['title']
        project.problem_description = request.form['problem_description']
        project.goal = request.form['goal']
        project.target_audience = request.form['target_audience']
        project.implementation_plan = request.form['implementation_plan']
        project.executor_info = request.form['executor_info']
        project.total_budget = request.form['total_budget']
        project.budget_breakdown = request.form['budget_breakdown']
        project.expected_result = request.form['expected_result']
        project.risks = request.form['risks']
        project.duration = request.form['duration']
        project.reporting_plan = request.form['reporting_plan']
        project.category = request.form.get('category')
        project.location = request.form.get('location')
        project.website = request.form.get('website')
        project.social_links = request.form.get('social_links')
        project.document_url = request.form.get('document_url')
        project.status = request.form.get('status')
        
        # Обрабатываем загрузку фото, если оно было предоставлено
        image_file = request.files.get('image_file')
        if image_file and image_file.filename:
            project.image_data = image_file.read()
            project.image_mimetype = image_file.mimetype
        
        db.session.commit()
        flash('Проєкт успішно оновлено!', 'success')
        return redirect(url_for('admin.dashboard'))
        
    return render_template('admin/edit_project.html', project=project)

@admin_bp.route('/delete_project/<int:project_id>', methods=['POST'])
@admin_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    db.session.delete(project)
    db.session.commit()
    flash('Проєкт успішно видалено!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/manage-founders', methods=['GET', 'POST'])
@admin_required
def manage_founders():
    """Manage founder users as an admin"""
    # Using string value for consistency since role is stored as string in DB
    founders = User.query.filter_by(role='founder').all()
    regular_members = User.query.filter_by(is_member=True).filter(User.role != 'founder').all()
    
    if request.method == 'POST':
        action = request.form.get('action')
        user_id = int(request.form.get('user_id'))
        user = User.query.get_or_404(user_id)
        
        if action == 'add':
            user.role = 'founder'
            flash(f'{user.email} успішно додано як засновника!', 'success')
        elif action == 'remove':
            user.role = 'member'
            flash(f'{user.email} видалено з засновників!', 'success')
        
        db.session.commit()
        return redirect(url_for('admin.manage_founders'))
    
    return render_template('admin/manage_founders.html', founders=founders, regular_members=regular_members)