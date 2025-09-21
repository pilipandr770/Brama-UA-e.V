import json
import os
from flask import session

def get_table_args():
    """
    Returns appropriate table arguments based on database configuration.
    If using PostgreSQL, includes schema specification; if using SQLite, returns empty dict.
    """
    # If DATABASE_URL is set, we're using PostgreSQL
    if os.getenv("DATABASE_URL"):
        return {'schema': os.getenv('DB_SCHEMA', 'brama')}
    # Otherwise, we're using SQLite which doesn't support schemas
    return {}

def get_translated_content(obj, field_name, default_field=None):
    """
    Get the translated version of a field based on the current language.
    
    Args:
        obj: The object (e.g., Block) that may have translations
        field_name: The name of the field to get (e.g., 'title', 'content')
        default_field: Optional default field to return if translation not found
        
    Returns:
        The translated content or the default content in Ukrainian
    """
    # Get current language from session
    lang = session.get('language', 'uk')
    
    # If the language is Ukrainian or the object doesn't have translations, return the default field
    if lang == 'uk' or not hasattr(obj, 'translations') or not obj.translations:
        return getattr(obj, default_field or field_name)
    
    try:
        translations = json.loads(obj.translations)
        if lang in translations and field_name in translations[lang]:
            translated = translations[lang][field_name]
            # Return the default field if the translation is empty
            if translated:
                return translated
    except (json.JSONDecodeError, AttributeError, KeyError):
        pass
    
    # Return the default field if translation not found
    return getattr(obj, default_field or field_name)
