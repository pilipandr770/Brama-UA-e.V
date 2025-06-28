#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script demonstrates the process of finding and wrapping translatable strings.
It can be used as a reference for how to properly internationalize Flask applications.
"""

from flask_babel import gettext as _

def example_flask_routes():
    """Example of wrapping strings in Flask routes"""
    # Flash messages should be wrapped with _()
    flash(_("Проєкт успішно подано!"))
    flash(_("Доступ лише для адміністратора!"))
    
    # Dynamic content with parameters
    error = "Database connection failed"
    flash(_("Помилка при збереженні: {}").format(error))
    
    # Success messages
    flash(_("Зустріч успішно створена!"))
    
    # Error messages
    flash(_("Можна редагувати лише заплановані зустрічі!"))
    
    # Return wrapped strings in rendered templates too
    return render_template('page.html', title=_("Головна сторінка"))

def example_jinja_templates():
    """Example of how to wrap strings in Jinja2 templates"""
    """
    In HTML templates:
    
    {# Page titles #}
    <title>{{ _("Політика конфіденційності") }}</title>
    
    {# Regular text content #}
    <p>{{ _("Ми, Brama UA e.V., поважаємо вашу приватність та захищаємо персональні дані відповідно до законодавства України та ЄС (GDPR).") }}</p>
    
    {# Form labels #}
    <label>{{ _("Ім'я*:") }}</label>
    
    {# Buttons #}
    <button>{{ _("Зберегти") }}</button>
    
    {# Placeholders #}
    <input placeholder="{{ _('Введіть ваше ім\'я') }}">
    
    {# Dynamic content with variables #}
    <p>{{ _("Вітаємо, %(name)s!", name=user.name) }}</p>
    
    {# Pluralization (uses ngettext) #}
    {{ ngettext('%(num)d проект', '%(num)d проекти', num) }}
    """
    pass

print("""
Important Notes for Translation in This Project:

1. Backend String Internationalization:
   - Import translation function: from flask_babel import gettext as _
   - Wrap user-visible strings: flash(_("Your message"))
   - For formatted strings: _("Error: {}").format(error_message)

2. Template String Internationalization:
   - Wrap visible text in templates: {{ _("Your text") }}
   - For HTML attributes: placeholder="{{ _('Enter your name') }}"

3. Updating Translations:
   - Extract strings: pybabel extract -F babel.cfg -k _l -o messages.pot app
   - Update language files: pybabel update -i messages.pot -d translations
   - Compile translations: pybabel compile -d translations

4. Add New Languages:
   - Initialize language: pybabel init -i messages.pot -d translations -l [lang_code]
   - Edit the PO file manually or with a script
   - Compile: pybabel compile -d translations

5. Check the TRANSLATIONS_GUIDE.md for more detailed instructions
""")
