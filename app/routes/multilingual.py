#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script adds multilingual support to the Block model, 
allowing administrators to create content in multiple languages.
"""

from flask import Blueprint, request, jsonify, session
from app.models.block import Block
from app import db
import json

multilingual_bp = Blueprint('multilingual', __name__)

@multilingual_bp.route('/api/translate-block/<int:block_id>', methods=['POST'])
def translate_block(block_id):
    """API endpoint to save translations for a block"""
    block = Block.query.get_or_404(block_id)
    language = request.form.get('language')
    title = request.form.get('title')
    content = request.form.get('content')
    
    if not language or language not in ['uk', 'de', 'en']:
        return jsonify({'error': 'Invalid language'}), 400
    
    # Initialize translations if not exists
    if not block.translations:
        block.translations = json.dumps({})
    
    translations = json.loads(block.translations)
    
    # Update translations for this language
    if language not in translations:
        translations[language] = {}
    
    translations[language]['title'] = title
    translations[language]['content'] = content
    
    # Save back to the database
    block.translations = json.dumps(translations)
    db.session.commit()
    
    return jsonify({'success': True})

def get_block_translation(block, language=None):
    """Helper function to get translated content for a block"""
    if not language:
        language = session.get('language', 'uk')
    
    # Default to Ukrainian
    if language == 'uk' or not block.translations:
        return block.title, block.content
    
    try:
        translations = json.loads(block.translations)
        if language in translations:
            title = translations[language].get('title') or block.title
            content = translations[language].get('content') or block.content
            return title, content
    except Exception:
        pass
    
    # Fall back to original content if translation missing
    return block.title, block.content
