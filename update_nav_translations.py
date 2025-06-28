#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to update translation files with additional translations for navigation elements.
"""

import re
import os

# Additional translations to include in both German and English files
ADDITIONAL_TRANSLATIONS = {
    "uk": {
        "Головна": "Головна",
        "Facebook": "Facebook",
        "Instagram": "Instagram",
        "Telegram": "Telegram",
        "Особистий кабінет": "Особистий кабінет",
        "Панель адміністратора": "Панель адміністратора",
        "Панель засновника": "Панель засновника",
        "Вийти": "Вийти",
        "Вхід": "Вхід",
        "Реєстрація": "Реєстрація"
    },
    "de": {
        "Головна": "Startseite",
        "Facebook": "Facebook",
        "Instagram": "Instagram",
        "Telegram": "Telegram",
        "Особистий кабінет": "Persönlicher Bereich",
        "Панель адміністратора": "Administrator-Panel",
        "Панель засновника": "Gründer-Panel",
        "Вийти": "Abmelden",
        "Вхід": "Anmelden",
        "Реєстрація": "Registrieren"
    },
    "en": {
        "Головна": "Home",
        "Facebook": "Facebook",
        "Instagram": "Instagram",
        "Telegram": "Telegram",
        "Особистий кабінет": "Personal Account",
        "Панель адміністратора": "Admin Panel",
        "Панель засновника": "Founder Panel",
        "Вийти": "Logout",
        "Вхід": "Login",
        "Реєстрація": "Register"
    }
}

def update_translations():
    """
    Extract all strings from base.html and update the translation files
    """
    print("Updating translation files...")
    
    # First, extract all strings
    os.system('pybabel extract -F babel.cfg -k _l -o messages.pot app')
    
    # Then update the translation files
    os.system('pybabel update -i messages.pot -d translations')
    
    # Now update the translation files with our additional translations
    for lang in ["de", "en"]:
        po_file_path = os.path.join('translations', lang, 'LC_MESSAGES', 'messages.po')
        
        with open(po_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # For each additional translation, find and update the corresponding entry
        for ukr_text, translated_text in ADDITIONAL_TRANSLATIONS[lang].items():
            # Create regex pattern to find the msgid/msgstr pair
            pattern = fr'msgid "{re.escape(ukr_text)}"\nmsgstr "(.*)?"'
            replacement = f'msgid "{ukr_text}"\nmsgstr "{translated_text}"'
            
            # Check if the msgid exists
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
            else:
                # If it doesn't exist, add it at the end of the file
                content += f'\n\nmsgid "{ukr_text}"\nmsgstr "{translated_text}"'
        
        # Write back to the file
        with open(po_file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Updated {lang} translations.")
    
    # Compile the translations
    os.system('pybabel compile -d translations')
    print("Translations compiled successfully.")

if __name__ == '__main__':
    update_translations()
