import argparse
from app import create_app, db
from app.models.user import User

def main():
    parser = argparse.ArgumentParser(description='Promote user to admin or create an admin user.')
    parser.add_argument('--email', required=False, help='User email to promote/create')
    parser.add_argument('--password', required=False, help='Password for new user (if creating)')
    parser.add_argument('--make-founder', action='store_true', help='Also set role to founder')
    args = parser.parse_args()

    app = create_app()
    with app.app_context():
        if not args.email:
            # Fallback to interactive
            email = input('Введіть email користувача, якого зробити адміністратором: ').strip()
        else:
            email = args.email.strip()

        user = User.query.filter_by(email=email).first()
        created = False
        if not user:
            if not args.password:
                print('Користувача не знайдено і пароль не передано. Використайте --password для створення нового користувача.')
                return
            # Create user
            user = User(email=email, is_member=True, is_admin=True, role='admin')
            try:
                user.set_password(args.password)
            except Exception:
                # set_password handles hashing; if fails, abort
                print('Помилка встановлення пароля. Операція скасована.')
                return
            db.session.add(user)
            created = True
        # Promote/update flags
        user.is_admin = True
        if args.make_founder:
            user.role = 'founder'
        elif not user.role:
            user.role = 'admin'
        db.session.commit()
        if created:
            print(f'Створено і призначено адміністратора: {email}')
        else:
            print(f'Користувача {email} призначено адміністратором')

if __name__ == '__main__':
    main()