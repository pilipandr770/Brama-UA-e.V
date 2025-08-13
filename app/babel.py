from flask import request, session, current_app
from flask_babel import Babel

# Initialize Babel without any configuration
babel = Babel()

def get_locale():
    # Try to get language from session first
    if 'language' in session:
        return session['language']
        
    # Otherwise, try to detect from browser settings
    return request.accept_languages.best_match(['uk', 'de', 'en'])

def init_babel(app):
    # Set translation directory configuration
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
    app.config['BABEL_DEFAULT_LOCALE'] = 'uk'
    app.config['BABEL_SUPPORTED_LOCALES'] = ['uk', 'de', 'en']
    
    # Initialize Babel with the app
    babel.init_app(app)
    
    # Set locale selector function
    babel.locale_selector_func = get_locale
    
    # Store babel instance on app for easier access
    app.babel_instance = babel
    
    # Define a function that will be used by templates and other code
    @app.context_processor
    def inject_babel_locale():
        return dict(get_locale=get_locale)
    
    # Override the Babel's internal get_locale function
    babel.locale_selector_func = get_locale
    
    return babel
