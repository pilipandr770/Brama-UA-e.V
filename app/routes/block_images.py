from flask import Blueprint, send_file, redirect, url_for
import io
from app.models.block import Block
from app.cache import cache

block_images_bp = Blueprint('block_images', __name__, url_prefix='/block-images')

@block_images_bp.route('/<int:block_id>')
@cache.cached(timeout=86400)  # Кэш на 24 часа для изображений блоков
def block_image_file(block_id):
    """
    Serve block image from database with caching
    """
    try:
        block = Block.query.get_or_404(block_id)
        
        # Если есть бинарные данные изображения в БД
        if block.image_data:
            response = send_file(
                io.BytesIO(block.image_data), 
                mimetype=block.image_mimetype
            )
            # Устанавливаем заголовок кэширования вручную с длительным сроком
            response.headers['Cache-Control'] = 'public, max-age=31536000'
            # Добавляем ETag для проверки изменений
            response.add_etag()
            return response
        # Иначе, если есть URL, перенаправляем на него
        elif block.image_url:
            return redirect(block.image_url)
        else:
            return '', 404
    except Exception as e:
        print(f"Error serving block image {block_id}: {str(e)}")
        return '', 500