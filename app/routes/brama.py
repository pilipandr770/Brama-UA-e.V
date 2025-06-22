from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.brama import Brama
from app import db

brama_bp = Blueprint('brama', __name__, url_prefix='/brama')

@brama_bp.route('/')
def index():
    """Главная страница для таблицы Brama"""
    brama_items = Brama.query.filter_by(is_active=True).all()
    return render_template('brama/index.html', brama_items=brama_items)

@brama_bp.route('/view/<int:id>')
def view(id):
    """Просмотр отдельного элемента таблицы Brama"""
    brama_item = Brama.query.get_or_404(id)
    return render_template('brama/view.html', brama_item=brama_item)

@brama_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Создание нового элемента таблицы Brama"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('Название обязательно для заполнения!', 'danger')
            return render_template('brama/create.html')
        
        new_brama = Brama(
            title=title,
            description=description
        )
        
        try:
            db.session.add(new_brama)
            db.session.commit()
            flash('Запись успешно создана!', 'success')
            return redirect(url_for('brama.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при сохранении: {str(e)}', 'danger')
    
    return render_template('brama/create.html')

@brama_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """Редактирование элемента таблицы Brama"""
    brama_item = Brama.query.get_or_404(id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        
        if not title:
            flash('Название обязательно для заполнения!', 'danger')
            return render_template('brama/edit.html', brama_item=brama_item)
        
        brama_item.title = title
        brama_item.description = description
        
        try:
            db.session.commit()
            flash('Запись успешно обновлена!', 'success')
            return redirect(url_for('brama.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при сохранении: {str(e)}', 'danger')
    
    return render_template('brama/edit.html', brama_item=brama_item)

@brama_bp.route('/delete/<int:id>')
def delete(id):
    """Удаление элемента таблицы Brama"""
    brama_item = Brama.query.get_or_404(id)
    
    try:
        db.session.delete(brama_item)
        db.session.commit()
        flash('Запись успешно удалена!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении: {str(e)}', 'danger')
    
    return redirect(url_for('brama.index'))
