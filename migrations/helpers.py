"""
This is a helper function for migrations to conditionally use schema
"""
import os

def use_schema():
    """Returns True if we should use schema (PostgreSQL), False for SQLite"""
    return bool(os.environ.get('DATABASE_URL'))