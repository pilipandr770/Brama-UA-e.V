from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    email = input('Введіть email користувача, якого зробити адміністратором: ')
    user = User.query.filter_by(email=email).first()
    if not user:
        print('Користувача з таким email не знайдено!')
    else:
        user.is_admin = True
        db.session.commit()
        print(f'Користувач {email} тепер адміністратор!') 