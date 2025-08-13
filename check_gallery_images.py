"""
Скрипт для проверки и восстановления изображений в базе данных
Это поможет диагностировать проблемы с изображениями
"""
import sys
import os
import io
from PIL import Image

# Добавляем родительский каталог в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, create_app
from app.models.gallery_image import GalleryImage

def check_gallery_images():
    """Проверяет все изображения галереи в базе данных"""
    app = create_app()
    with app.app_context():
        images = GalleryImage.query.all()
        print(f"Всего найдено {len(images)} изображений в галерее")
        
        valid_images = 0
        invalid_images = 0
        url_only_images = 0
        empty_images = 0
        
        for idx, img in enumerate(images):
            print(f"\nИзображение {idx+1}/{len(images)} (ID: {img.id}):")
            print(f"  Block ID: {img.block_id}")
            print(f"  Description: {img.description}")
            
            if img.image_data:
                print(f"  Image data: {len(img.image_data)} bytes")
                print(f"  MIME-type: {img.image_mimetype}")
                
                # Проверяем, можно ли открыть изображение
                try:
                    image = Image.open(io.BytesIO(img.image_data))
                    print(f"  Size: {image.size[0]}x{image.size[1]}")
                    print(f"  Format: {image.format}")
                    valid_images += 1
                except Exception as e:
                    print(f"  ERROR: Cannot open image: {str(e)}")
                    invalid_images += 1
            elif img.image_url:
                print(f"  Image URL: {img.image_url}")
                url_only_images += 1
            else:
                print("  ERROR: No image data or URL!")
                empty_images += 1
        
        print("\nСводка:")
        print(f"Всего изображений: {len(images)}")
        print(f"Валидных BLOB-изображений: {valid_images}")
        print(f"Невалидных BLOB-изображений: {invalid_images}")
        print(f"Только URL (без BLOB): {url_only_images}")
        print(f"Пустых изображений (без BLOB и URL): {empty_images}")

if __name__ == "__main__":
    check_gallery_images()
