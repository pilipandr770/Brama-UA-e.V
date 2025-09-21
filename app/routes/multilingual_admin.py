from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from app import db
from app.models.block import Block
import json
from functools import wraps
from app.routes.admin import admin_required

multilingual_admin_bp = Blueprint('multilingual_admin', __name__, url_prefix='/admin/multilingual')

@multilingual_admin_bp.route('/block/edit/<int:block_id>', methods=['GET', 'POST'])
@admin_required
def edit_block_multilingual(block_id):
    """Edit block with multilingual support"""
    block = Block.query.get_or_404(block_id)
    
    if request.method == 'POST':
        # Get Ukrainian (default) content
        block.title = request.form['title']
        block.content = request.form['content']
        block.type = request.form['type']
        
        # Process translations
        translations = {}
        if hasattr(block, 'translations') and block.translations:
            try:
                translations = json.loads(block.translations)
            except json.JSONDecodeError:
                translations = {}
        
        # Process German translations
        if 'title_de' in request.form or 'content_de' in request.form:
            if 'de' not in translations:
                translations['de'] = {}
            
            if request.form.get('title_de'):
                translations['de']['title'] = request.form['title_de']
            
            if request.form.get('content_de'):
                translations['de']['content'] = request.form['content_de']
        
        # Process English translations
        if 'title_en' in request.form or 'content_en' in request.form:
            if 'en' not in translations:
                translations['en'] = {}
            
            if request.form.get('title_en'):
                translations['en']['title'] = request.form['title_en']
            
            if request.form.get('content_en'):
                translations['en']['content'] = request.form['content_en']
        
        # Save translations as JSON string
        block.translations = json.dumps(translations)
        
        # Process image uploads - сохраняем и в БД и на диск для надежности
        image_file = request.files.get('image_file')
        if image_file and image_file.filename:
            # Generate unique filename
            import os
            from werkzeug.utils import secure_filename
            from datetime import datetime
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Create unique filename
            filename = secure_filename(image_file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Сохраняем изображение в базе данных
            image_data = image_file.read()
            block.image_data = image_data
            block.image_mimetype = image_file.mimetype
            
            # Сохраняем также файл на диск для совместимости
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Устанавливаем URL для совместимости
            block.image_url = url_for('static', filename=f'uploads/{unique_filename}')
        else:
            # If no file uploaded, use URL from form
            image_url = request.form.get('image_url')
            if image_url:
                block.image_url = image_url
        
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    
    # For GET request, prepare translations for template
    translations = {'de': {}, 'en': {}}
    
    if hasattr(block, 'translations') and block.translations:
        try:
            saved_translations = json.loads(block.translations)
            if 'de' in saved_translations:
                translations['de'] = saved_translations['de']
            if 'en' in saved_translations:
                translations['en'] = saved_translations['en']
        except json.JSONDecodeError:
            pass
    
    # Add translations to block for template rendering
    block.translations = translations
    
    return render_template('admin/edit_block_multilingual.html', block=block)

@multilingual_admin_bp.route('/block/create', methods=['GET', 'POST'])
@admin_required
def create_block_multilingual():
    """Create a new block with multilingual support"""
    if request.method == 'POST':
        # Create new block with Ukrainian (default) content
        block = Block(
            title=request.form['title'],
            content=request.form['content'],
            type=request.form['type'],
            is_active=True
        )
        
        # Process translations
        translations = {}
        
        # Process German translations
        if 'title_de' in request.form or 'content_de' in request.form:
            translations['de'] = {}
            
            if request.form.get('title_de'):
                translations['de']['title'] = request.form['title_de']
            
            if request.form.get('content_de'):
                translations['de']['content'] = request.form['content_de']
        
        # Process English translations
        if 'title_en' in request.form or 'content_en' in request.form:
            translations['en'] = {}
            
            if request.form.get('title_en'):
                translations['en']['title'] = request.form['title_en']
            
            if request.form.get('content_en'):
                translations['en']['content'] = request.form['content_en']
        
        # Save translations as JSON string if there are any
        if translations:
            block.translations = json.dumps(translations)
        
        # Process image uploads - сохраняем и в БД и на диск для надежности
        image_file = request.files.get('image_file')
        if image_file and image_file.filename:
            # Generate unique filename
            import os
            from werkzeug.utils import secure_filename
            from datetime import datetime
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(os.getcwd(), 'app', 'static', 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            # Create unique filename
            filename = secure_filename(image_file.filename)
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(upload_dir, unique_filename)
            
            # Сохраняем изображение в базе данных
            image_data = image_file.read()
            block.image_data = image_data
            block.image_mimetype = image_file.mimetype
            
            # Сохраняем также файл на диск для совместимости
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            # Устанавливаем URL для совместимости
            block.image_url = url_for('static', filename=f'uploads/{unique_filename}')
        else:
            # If no file uploaded, use URL from form
            image_url = request.form.get('image_url')
            if image_url:
                block.image_url = image_url
        
        db.session.add(block)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_block_multilingual.html', block=None)
