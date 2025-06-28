#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to edit the English translations file with translated strings.
This script reads the messages.po file, translates all empty msgstr entries,
and writes the result back to the messages.po file.
"""

import re
import os

# Dictionary of Ukrainian to English translations
TRANSLATIONS = {
    # Routes messages (flash messages)
    "Проєкт успішно подано! Очікує модерації.": "Project submitted successfully! Awaiting moderation.",
    "Помилка при збереженні: {}": "Error saving: {}",
    "Користувач з такою поштою вже існує.": "A user with this email already exists.",
    "Реєстрація успішна! Ви стали членом ферайну.": "Registration successful! You are now a member of the association.",
    "Ви увійшли!": "You are logged in!",
    "Невірний email або пароль": "Invalid email or password",
    "Ви вийшли з акаунту.": "You have been logged out.",
    "Увійдіть, щоб побачити кабінет": "Please log in to see the dashboard",
    "Треба увійти, щоб голосувати.": "You must be logged in to vote.",
    "Ви вже підтримали цей проєкт!": "You have already supported this project!",
    "Ваш голос зараховано!": "Your vote has been counted!",
    "Увійдіть, щоб змінити фото профілю": "Log in to change your profile photo",
    "Користувача не знайдено": "User not found",
    "Файл не вибрано": "No file selected",
    "Фото профілю оновлено": "Profile photo updated",

    # Base template
    "Brama UA": "Brama UA",
    "Політика конфіденційності": "Privacy Policy",
    "Контакти": "Contacts",
    "Імпресум": "Impressum",

    # Contact page
    "Зв'яжіться з нами для співпраці, питань чи пропозицій:": "Contact us for cooperation, questions or suggestions:",
    "Email:": "Email:",
    "Телефон:": "Phone:",
    "Адреса:": "Address:",
    "Берлін, Німеччина": "Berlin, Germany",
    "Або скористайтесь формою:": "Or use the form:",
    "Ваше ім'я:": "Your name:",
    "Повідомлення:": "Message:",
    "Надіслати": "Send",

    # Index page
    "Головна сторінка": "Home Page",

    # Login page
    "Вхід": "Login",
    "Email": "Email",
    "Пароль": "Password",
    "Увійти": "Log in",

    # Register page
    "Реєстрація члена ферайну / волонтера": "Register as association member / volunteer",
    "Згода на обробку персональних даних (GDPR):": "Consent to personal data processing (GDPR):",
    "Ваша інформація буде використана лише для членства у ферайні, комунікації, організації волонтерської діяльності та звітності. Дані не передаються третім особам, окрім випадків, передбачених законом. Ви маєте право на доступ, зміну та видалення своїх даних. Детальніше — у": 
    "Your information will only be used for association membership, communication, organizing volunteer activities and reporting. Data is not shared with third parties, except as required by law. You have the right to access, modify and delete your data. More details in the",
    "Політиці конфіденційності": "Privacy Policy",
    "Погоджуюсь": "I agree",
    "Ім'я*:": "First name*:",
    "Прізвище*:": "Last name*:",
    "Дата народження*:": "Date of birth*:",
    "Спеціальність:": "Specialty:",
    "Мета приєднання до ферайну*:": "Purpose of joining the association*:",
    "Чим можете допомогти?": "How can you help?",
    "Чим хочете займатись?": "What would you like to do?",
    "Телефон*:": "Phone*:",
    "Email*:": "Email*:",
    "Пароль*:": "Password*:",
    "Зареєструватися": "Register",

    # Submit project page
    "Подати проєкт": "Submit Project",
    "Подати новий соціальний проєкт": "Submit a new social project",
    "Назва проєкту*": "Project name*",
    "Опис проблеми*": "Problem description*",
    "Мета*": "Goal*",
    "Цільова аудиторія*": "Target audience*",
    "План реалізації*": "Implementation plan*",
    "Виконавець*": "Implementer*",
    "Бюджет (€)*": "Budget (€)*",
    "Розподіл бюджету*": "Budget distribution*",
    "Очікуваний результат*": "Expected result*",
    "Можливі ризики*": "Possible risks*",
    "Тривалість*": "Duration*",
    "Звітність*": "Reporting*",
    "Категорія": "Category",
    "Місце реалізації": "Implementation location",
    "Вебсайт": "Website",
    "Соцмережі": "Social networks",
    "Фото проєкту (необовʼязково):": "Project photo (optional):",
    "Документ (URL)": "Document (URL)",
}

def translate_po_file(po_file_path):
    """
    Translate empty msgstr entries in the PO file using the TRANSLATIONS dictionary
    """
    with open(po_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find message blocks (msgid followed by msgstr)
    pattern = r'(msgid "(.+?)"\nmsgstr ")(")'
    
    def replace_translation(match):
        msgid = match.group(2)
        if msgid in TRANSLATIONS:
            return f'{match.group(1)}{TRANSLATIONS[msgid]}{match.group(3)}'
        return match.group(0)
    
    # Replace empty msgstr with translations
    translated_content = re.sub(pattern, replace_translation, content)
    
    # Write back to the file
    with open(po_file_path, 'w', encoding='utf-8') as f:
        f.write(translated_content)
    
    print(f"Translations applied to {po_file_path}")

if __name__ == '__main__':
    po_file_path = os.path.join('translations', 'en', 'LC_MESSAGES', 'messages.po')
    translate_po_file(po_file_path)
