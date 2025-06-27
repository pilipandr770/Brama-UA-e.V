import os
from flask import Flask
from app import create_app, db, socketio
from app.models import User

app = create_app()
app.secret_key = os.getenv('SECRET_KEY', 'secret')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, host='0.0.0.0', port=port, debug=True)
