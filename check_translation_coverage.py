#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script checks for strings in templates and Python files that might need translation
but are not yet wrapped in _() or gettext().
"""

import os
import re
import glob

def find_potential_translations_in_python(file_path):
    """Find potential translatable strings in Python files that aren't wrapped in _()"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for flash messages and other strings that might need translation
    flash_pattern = r'flash\((["\'])((?:(?!\1).)+)\1'
    flash_matches = re.findall(flash_pattern, content)
    
    # Check if these flash messages are already wrapped in _()
    gettext_pattern = r'flash\(_\((["\'])((?:(?!\1).)+)\1\)'
    gettext_matches = re.findall(gettext_pattern, content)
    
    unwrapped_strings = []
    for quote, message in flash_matches:
        if not any(message in wrapped for quote, wrapped in gettext_matches):
            if not message.startswith('_'):  # Skip if already using _()
                unwrapped_strings.append(message)
    
    return unwrapped_strings

def find_potential_translations_in_template(file_path):
    """Find potential translatable strings in template files that aren't wrapped in {{ _() }}"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Look for text in tags that might need translation
    # This is a simple heuristic and might have false positives
    tag_content_pattern = r'>([^<>{}]{5,})<'
    tag_matches = re.findall(tag_content_pattern, content)
    
    # Check if these strings are already wrapped in {{ _() }}
    gettext_pattern = r'{{ _\((["\'])((?:(?!\1).)+)\1\) }}'
    gettext_matches = re.findall(gettext_pattern, content)
    
    unwrapped_strings = []
    for text in tag_matches:
        text = text.strip()
        # Skip if mostly numbers or special characters
        if len(re.sub(r'[^a-zA-Zа-яА-ЯіІїЇєЄґҐʼ]', '', text)) < 5:
            continue
        
        # Skip if it seems to be a Jinja2 variable or expression
        if '{{' in text or '{%' in text:
            continue
            
        # Check if this text is already wrapped in _()
        wrapped = False
        for quote, wrapped_text in gettext_matches:
            if text in wrapped_text:
                wrapped = True
                break
        
        if not wrapped:
            unwrapped_strings.append(text)
    
    return unwrapped_strings

def main():
    print("Checking for potential untranslated strings...")
    
    # Check Python files
    python_files = glob.glob('app/**/*.py', recursive=True)
    print("\n=== PYTHON FILES ===")
    for py_file in python_files:
        unwrapped = find_potential_translations_in_python(py_file)
        if unwrapped:
            print(f"\nIn {py_file}:")
            for s in unwrapped:
                print(f"  - {s}")
    
    # Check Template files
    template_files = glob.glob('app/templates/**/*.html', recursive=True)
    print("\n=== TEMPLATE FILES ===")
    for tmpl_file in template_files:
        unwrapped = find_potential_translations_in_template(tmpl_file)
        if unwrapped:
            print(f"\nIn {tmpl_file}:")
            for s in unwrapped:
                print(f"  - {s}")
    
    print("\nDone. Remember that this tool may show false positives and miss some strings.")
    print("Always manually review files to ensure proper translation coverage.")

if __name__ == "__main__":
    main()
