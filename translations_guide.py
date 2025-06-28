from flask import Flask, render_template, request, session, redirect, url_for
from flask_babel import Babel, gettext as _

# Example of how to use translations in your templates and Python code:
# 
# In Python:
# from flask_babel import gettext as _
# flash(_('Welcome to the site!'), 'success')
# 
# In templates:
# <h1>{{ _('Hello World') }}</h1>
# <p>{{ _('Welcome to our website') }}</p>

# To extract messages for translation:
# 1. Run: pybabel extract -F babel.cfg -o messages.pot .
# 2. Initialize a language: pybabel init -i messages.pot -d translations -l de
# 3. Edit the translations/de/LC_MESSAGES/messages.po file
# 4. Compile: pybabel compile -d translations
# 
# To update existing translations after adding new strings:
# 1. Extract new messages: pybabel extract -F babel.cfg -o messages.pot .
# 2. Update existing translations: pybabel update -i messages.pot -d translations
# 3. Edit the .po files again
# 4. Compile: pybabel compile -d translations
