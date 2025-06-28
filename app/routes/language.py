from flask import Blueprint, session, redirect, url_for, request

language_bp = Blueprint('language', __name__)

@language_bp.route('/set-language/<language>')
def set_language(language):
    # Store the user's language preference in the session
    session['language'] = language
    
    # Redirect back to the referring page, or to the homepage if no referrer
    referrer = request.referrer or url_for('main.index')
    return redirect(referrer)
