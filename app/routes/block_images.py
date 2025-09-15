from flask import Blueprint, send_file, redirect, url_for
import io
from app.models.block import Block

block_images_bp = Blueprint('block_images', __name__, url_prefix='/block-images')

@block_images_bp.route('/<int:block_id>')
def block_image_file(block_id):
    """
    Serve block image from database
    """
    try:
        block = Block.query.get_or_404(block_id)
        
        # Если есть бинарные данные изображения в БД
        if block.image_data:
            return send_file(
                io.BytesIO(block.image_data), 
                mimetype=block.image_mimetype, 
                cache_timeout=31536000  # 1 год кеширования
            )
        # Иначе, если есть URL, перенаправляем на него
        elif block.image_url:
            return redirect(block.image_url)
        else:
            return '', 404
    except Exception as e:
        print(f"Error serving block image {block_id}: {str(e)}")
        return '', 500