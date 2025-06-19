app.secret_key = os.getenv('SECRET_KEY', 'secret')
from flask import Flask
from app import create_app, db
from app.models import User
