from flask import Blueprint, render_template, redirect, url_for, session, flash, request
from app import db
from app.models.user import User
from app.models.block import Block
from app.models.gallery_image import GalleryImage
from app.models.project import Project
from app.models.settings import Settings
from app.models.report import Report
from functools import wraps

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
        block = Block(title=title, content=content, type=type_, image_url=image_url)
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
        block.image_url = request.form.get('image_url')
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
        image_url = request.form['image_url']
        description = request.form['description']
        block_id = request.form.get('block_id')
        img = GalleryImage(image_url=image_url, description=description, block_id=block_id)
        db.session.add(img)
        db.session.commit()
        flash('Фото додано до галереї!', 'success')
        return redirect(url_for('admin.dashboard'))
    blocks = Block.query.filter_by(type='gallery').all()
    return render_template('admin/add_gallery_image.html', blocks=blocks)

@admin_bp.route('/gallery/delete/<int:image_id>', methods=['POST'])
@admin_required
def delete_gallery_image(image_id):
    img = GalleryImage.query.get_or_404(image_id)
    db.session.delete(img)
    db.session.commit()
    flash('Фото видалено з галереї!', 'success')
    return redirect(url_for('admin.dashboard')) 