#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script helps prepare your Flask app for internationalization
by finding and wrapping text strings with _() function.
It identifies potential translation targets in:
1. Python files - string literals and variable assignments
2. Templates - text nodes and attribute values that might need translation
"""

import os
import re
import sys
from pathlib import Path

# Directories to check
PYTHON_DIRS = ['app']
TEMPLATE_DIRS = ['app/templates']
EXCLUDE_DIRS = ['__pycache__', 'static', 'venv']

# File extensions to check
PYTHON_EXT = ['.py']
TEMPLATE_EXT = ['.html']

# Regular expressions for finding text in Python files
# This is a simplified approach - it won't catch everything but helps identify candidates
PY_STRING_REGEX = r'(?<![_\.a-zA-Z0-9])[\'\"]{1,3}([^\'\"\n]+)[\'\"]{1,3}'
PY_ASSIGNMENT_REGEX = r'([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*[\'\"]{1,3}([^\'\"\n]+)[\'\"]{1,3}'

# Regular expressions for finding text in HTML templates
HTML_TEXT_REGEX = r'>([^<>\n\{\}]+)<'  # Text between tags
HTML_ATTR_REGEX = r'(title|placeholder|alt|aria-label)=[\'"]([^\'"]+)[\'"]'  # Common translatable attributes


def find_strings_in_python_file(file_path):
    """Find potential strings for translation in Python files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Find string literals - this is simplified and won't catch everything
    string_matches = re.finditer(PY_STRING_REGEX, content)
    for match in string_matches:
        string_text = match.group(1)
        # Skip strings that are likely not user-facing
        if (len(string_text) > 3 and  # Skip short strings
            not string_text.startswith('_') and 
            not string_text.startswith('/') and  # Skip URLs
            not string_text.startswith('http') and
            not string_text.startswith('#') and
            not re.match(r'^[A-Z_]+$', string_text) and  # Skip constants
            ' ' in string_text):  # Probably a sentence
                
            print(f"In {file_path}:")
            print(f"  Found potential text: '{string_text}'")
            print(f"  Consider: _('{string_text}')")
            print()


def find_strings_in_template(file_path):
    """Find potential strings for translation in template files."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find text between tags
    text_matches = re.finditer(HTML_TEXT_REGEX, content)
    for match in text_matches:
        text = match.group(1).strip()
        if text and len(text) > 3 and not text.startswith('{{') and not text.startswith('{%'):
            print(f"In {file_path}:")
            print(f"  Found text node: '{text}'")
            print(f"  Consider: {{ _('{text}') }}")
            print()
    
    # Find translatable attributes
    attr_matches = re.finditer(HTML_ATTR_REGEX, content)
    for match in attr_matches:
        attr_name = match.group(1)
        attr_value = match.group(2)
        if attr_value and len(attr_value) > 3 and not attr_value.startswith('{{'):
            print(f"In {file_path}:")
            print(f"  Found attribute {attr_name}='{attr_value}'")
            print(f"  Consider: {attr_name}=\"{{ _('{attr_value}') }}\"")
            print()


def scan_directory(directory, extensions, scan_function):
    """Scan directory recursively for files with given extensions and apply scan_function."""
    for root, dirs, files in os.walk(directory):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                scan_function(file_path)


def main():
    """Main function to scan files for translation candidates."""
    print("Scanning Python files for translation candidates...")
    for directory in PYTHON_DIRS:
        if os.path.exists(directory):
            scan_directory(directory, PYTHON_EXT, find_strings_in_python_file)
    
    print("\nScanning templates for translation candidates...")
    for directory in TEMPLATE_DIRS:
        if os.path.exists(directory):
            scan_directory(directory, TEMPLATE_EXT, find_strings_in_template)


if __name__ == "__main__":
    main()
