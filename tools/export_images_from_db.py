# Файл: tools/export_images_from_db.py
import os, pathlib, time
from werkzeug.utils import secure_filename
from app import app, db
from app.models.block import Block
from app.models.gallery_image import GalleryImage

UPLOAD_DIR = pathlib.Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _ext_from_mime(mime):
    if not mime: return ".bin"
    mime = mime.lower()
    if "png" in mime: return ".png"
    if "jpeg" in mime or "jpg" in mime: return ".jpg"
    if "webp" in mime: return ".webp"
    if "gif" in mime: return ".gif"
    return ".bin"

def export_blocks():
    cnt = 0
    for b in Block.query.all():
        if getattr(b, "image_data", None):
            ext = _ext_from_mime(getattr(b, "image_mimetype", None))
            name = f"block_{b.id}_{int(time.time())}{ext}"
            path = UPLOAD_DIR / secure_filename(name)
            with open(path, "wb") as f:
                f.write(b.image_data)
            b.image_url = f"/static/uploads/{name}"
            b.image_data = None
            b.image_mimetype = None
            cnt += 1
    db.session.commit()
    return cnt

def export_gallery():
    cnt = 0
    for g in GalleryImage.query.all():
        if getattr(g, "image_data", None):
            ext = _ext_from_mime(getattr(g, "image_mimetype", None))
            name = f"gallery_{g.id}_{int(time.time())}{ext}"
            path = UPLOAD_DIR / secure_filename(name)
            with open(path, "wb") as f:
                f.write(g.image_data)
            g.image_url = f"/static/uploads/{name}"
            g.image_data = None
            g.image_mimetype = None
            cnt += 1
    db.session.commit()
    return cnt

if __name__ == "__main__":
    with app.app_context():
        b = export_blocks()
        g = export_gallery()
        print(f"Exported blocks: {b}, gallery images: {g}")