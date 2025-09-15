"""исправление для модели Block

Этот файл создает маппинг для SQLAlchemy, который позволяет 
обойтись без обязательных полей name и slug в таблице blocks.
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Boolean

# Минимальный маппинг для таблицы blocks
class MinimalBlock(declarative_base()):
    __tablename__ = 'blocks'
    __table_args__ = {'schema': 'brama'}
    
    id = Column(Integer, primary_key=True)
    title = Column(String(128), nullable=False)
    content = Column(Text, nullable=True)
    type = Column(String(32), nullable=False)
    is_active = Column(Boolean, default=True)
    image_url = Column(String(300), nullable=True)
    translations = Column(Text, nullable=True)