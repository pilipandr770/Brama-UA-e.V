from app import app, db
from app.models.block import Block

with app.app_context():
    block = Block.query.get(8)
    if block:
        print(f'Block {block.id}: type={block.type}, title={block.title}, is_active={block.is_active}')
    else:
        print('Block 8 not found')