#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to edit the German translations file with translated strings.
This script reads the messages.po file, translates all empty msgstr entries,
and writes the result back to the messages.po file.
"""

import re
import os

# Dictionary of Ukrainian to German translations
TRANSLATIONS = {
    # Routes messages (flash messages)
    "Проєкт успішно подано! Очікує модерації.": "Projekt erfolgreich eingereicht! Wartet auf Moderation.",
    "Помилка при збереженні: {}": "Fehler beim Speichern: {}",
    "Користувач з такою поштою вже існує.": "Ein Benutzer mit dieser E-Mail existiert bereits.",
    "Реєстрація успішна! Ви стали членом ферайну.": "Registrierung erfolgreich! Sie sind jetzt Mitglied des Vereins.",
    "Ви увійшли!": "Sie sind angemeldet!",
    "Невірний email або пароль": "Ungültige E-Mail oder Passwort",
    "Ви вийшли з акаунту.": "Sie haben sich abgemeldet.",
    "Увійдіть, щоб побачити кабінет": "Bitte melden Sie sich an, um das Dashboard zu sehen",
    "Треба увійти, щоб голосувати.": "Sie müssen angemeldet sein, um abzustimmen.",
    "Ви вже підтримали цей проєкт!": "Sie haben dieses Projekt bereits unterstützt!",
    "Ваш голос зараховано!": "Ihre Stimme wurde gezählt!",
    "Увійдіть, щоб змінити фото профілю": "Melden Sie sich an, um Ihr Profilbild zu ändern",
    "Користувача не знайдено": "Benutzer nicht gefunden",
    "Файл не вибрано": "Keine Datei ausgewählt",
    "Фото профілю оновлено": "Profilbild aktualisiert",

    # Base template
    "Brama UA": "Brama UA",
    "Політика конфіденційності": "Datenschutzerklärung",
    "Контакти": "Kontakte",
    "Імпресум": "Impressum",

    # Contact page
    "Зв'яжіться з нами для співпраці, питань чи пропозицій:": "Kontaktieren Sie uns für Zusammenarbeit, Fragen oder Vorschläge:",
    "Email:": "E-Mail:",
    "Телефон:": "Telefon:",
    "Адреса:": "Adresse:",
    "Берлін, Німеччина": "Berlin, Deutschland",
    "Або скористайтесь формою:": "Oder benutzen Sie das Formular:",
    "Ваше ім'я:": "Ihr Name:",
    "Повідомлення:": "Nachricht:",
    "Надіслати": "Absenden",

    # Index page
    "Головна сторінка": "Startseite",

    # Login page
    "Вхід": "Anmeldung",
    "Email": "E-Mail",
    "Пароль": "Passwort",
    "Увійти": "Anmelden",

    # Register page
    "Реєстрація члена ферайну / волонтера": "Registrierung eines Vereinsmitglieds / Freiwilligen",
    "Згода на обробку персональних даних (GDPR):": "Einwilligung zur Verarbeitung personenbezogener Daten (DSGVO):",
    "Ваша інформація буде використана лише для членства у ферайні, комунікації, організації волонтерської діяльності та звітності. Дані не передаються третім особам, окрім випадків, передбачених законом. Ви маєте право на доступ, зміну та видалення своїх даних. Детальніше — у": 
    "Ihre Daten werden nur für die Vereinsmitgliedschaft, Kommunikation, Organisation von Freiwilligentätigkeiten und Berichterstattung verwendet. Die Daten werden nicht an Dritte weitergegeben, außer in gesetzlich vorgesehenen Fällen. Sie haben das Recht auf Zugang, Änderung und Löschung Ihrer Daten. Weitere Informationen finden Sie in der",
    "Політиці конфіденційності": "Datenschutzerklärung",
    "Погоджуюсь": "Ich stimme zu",
    "Ім'я*:": "Vorname*:",
    "Прізвище*:": "Nachname*:",
    "Дата народження*:": "Geburtsdatum*:",
    "Спеціальність:": "Fachgebiet:",
    "Мета приєднання до ферайну*:": "Zweck des Vereinsbeitritts*:",
    "Чим можете допомогти?": "Wie können Sie helfen?",
    "Чим хочете займатись?": "Womit möchten Sie sich beschäftigen?",
    "Телефон*:": "Telefon*:",
    "Email*:": "E-Mail*:",
    "Пароль*:": "Passwort*:",
    "Зареєструватися": "Registrieren",

    # Submit project page
    "Подати проєкт": "Projekt einreichen",
    "Подати новий соціальний проєкт": "Neues soziales Projekt einreichen",
    "Назва проєкту*": "Projektname*",
    "Опис проблеми*": "Problembeschreibung*",
    "Мета*": "Ziel*",
    "Цільова аудиторія*": "Zielgruppe*",
    "План реалізації*": "Umsetzungsplan*",
    "Виконавець*": "Ausführender*",
    "Бюджет (€)*": "Budget (€)*",
    "Розподіл бюджету*": "Budgetverteilung*",
    "Очікуваний результат*": "Erwartetes Ergebnis*",
    "Можливі ризики*": "Mögliche Risiken*",
    "Тривалість*": "Dauer*",
    "Звітність*": "Berichterstattung*",
    "Категорія": "Kategorie",
    "Місце реалізації": "Umsetzungsort",
    "Вебсайт": "Website",
    "Соцмережі": "Soziale Netzwerke",
    "Фото проєкту (необовʼязково):": "Projektfoto (optional):",
    "Документ (URL)": "Dokument (URL)",
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
    po_file_path = os.path.join('translations', 'de', 'LC_MESSAGES', 'messages.po')
    translate_po_file(po_file_path)
