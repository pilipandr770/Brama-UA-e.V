from app import app, db
from app.models.block import Block

with app.app_context():
    blocks = Block.query.all()
    print(f'Found {len(blocks)} blocks:')
    for b in blocks:
        print(f'Block {b.id}: title={b.title}, has_image_data={b.image_data is not None}, image_url={b.image_url}')