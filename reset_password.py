from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    email = input('Введіть email користувача для скидання пароля: ')
    user = User.query.filter_by(email=email).first()
    if not user:
        print('Користувача з таким email не знайдено!')
    else:
        new_password = input('Введіть новий пароль: ')
        user.set_password(new_password)
        db.session.commit()
        print(f'Пароль для користувача {email} оновлено!')
