# Translation Guide for Brama UA e.V. Website

This document provides a guide on how to manage translations for the Brama UA e.V. website.

## Overview

The website supports multiple languages using Flask-Babel. Currently, the following languages are available:
- Ukrainian (uk) - Default language
- German (de)
- English (en)

## Translation Components

The website has two types of translatable content:

1. **Interface translations**: Static text elements like buttons, labels, and messages that are part of the application interface. These are managed with Flask-Babel.

2. **Dynamic content translations**: Content created by administrators (like blocks, news, etc.) that can be edited in multiple languages through the admin interface.

## File Structure

- `babel.cfg`: Configuration file for Babel extraction
- `messages.pot`: Template file containing all translatable strings
- `translations/`: Directory containing translation files for each language
  - `de/LC_MESSAGES/messages.po`: German translations
  - `en/LC_MESSAGES/messages.po`: English translations
  - `*.mo`: Compiled translation files (binary)
- `MULTILINGUAL_GUIDE.md`: Guide for administrators on managing multilingual content

## Workflow for Adding or Updating Translations

### 1. Extract Translatable Strings

When new translatable strings are added to the application (in Python files or templates), extract them to update the POT template:

```bash
pybabel extract -F babel.cfg -k _l -o messages.pot app
```

### 2. Update Existing Translations

Update the existing language files with new strings:

```bash
pybabel update -i messages.pot -d translations
```

### 3. Translate New Strings

Edit the `.po` files in the `translations/[language]/LC_MESSAGES/` directory. You can use a text editor or specialized tools like Poedit.

For automated translation, you can use the provided scripts:
- `python translate_messages.py` - For German translations
- `python translate_messages_en.py` - For English translations

### 4. Compile Translations

After editing translations, compile them to `.mo` files that the application will use:

```bash
pybabel compile -d translations
```

## Adding a New Language

To add support for a new language:

1. Initialize the translation files for the new language (e.g., French 'fr'):

```bash
pybabel init -i messages.pot -d translations -l fr
```

2. Edit the translations in `translations/fr/LC_MESSAGES/messages.po`

3. Create a new translation script (optional)

4. Compile the translations:

```bash
pybabel compile -d translations
```

5. Update the language switcher in `app/templates/base.html` to include the new language

## Best Practices for Translatable Strings

### In Python Files

```python
from flask_babel import gettext as _

# Use _ function for translatable strings
flash(_("Реєстрація успішна! Ви стали членом ферайну."))
```

### In Jinja2 Templates

```html
<h1>{{ _("Подати проєкт") }}</h1>
<p>{{ _("Зв'яжіться з нами для співпраці, питань чи пропозицій:") }}</p>
```

## Maintaining Translations

- Regularly extract strings and update translations when making changes
- Always compile translations after making changes to .po files
- Test all supported languages after updating translations

## Language Detection

The application will select a language based on:
1. User's explicit choice (stored in session)
2. Browser's language preferences
3. Default to Ukrainian if no preference is detected

## Troubleshooting

If translations aren't showing up:
- Make sure translations are compiled (`pybabel compile -d translations`)
- Check if the language is properly set in the session or browser
- Verify that the translatable strings are wrapped correctly with `_()` or `_()`
- Restart the Flask application to load the latest translations
