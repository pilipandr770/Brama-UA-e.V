# Simple route handler for the index page that avoids database errors
from flask import Flask, render_template, Blueprint
from sqlalchemy.exc import OperationalError
import os

# Create the Flask app
app = Flask(__name__, 
           template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates'),
           static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'))

# Set up the database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(os.path.dirname(os.path.dirname(__file__)), "site.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy(app)

# Define a simple error handler route
@app.route('/')
def index():
    return render_template('error.html', 
                          error_title="System Maintenance", 
                          error_message="The site is currently undergoing maintenance. Please try again later.")

@app.route('/login')
def login():
    return render_template('error.html', 
                          error_title="System Maintenance", 
                          error_message="The login system is currently undergoing maintenance. Please try again later.")

@app.route('/register')
def register():
    return render_template('error.html', 
                          error_title="System Maintenance", 
                          error_message="The registration system is currently undergoing maintenance. Please try again later.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
