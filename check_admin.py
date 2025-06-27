from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if admin users exist and create one if needed
    admin_users = User.query.filter_by(is_admin=True).all()
    
    print(f"Found {len(admin_users)} admin users:")
    for admin in admin_users:
        print(f"- ID: {admin.id}, Email: {admin.email}, Is Admin: {admin.is_admin}")
    
    # If no admin users, create one
    if not admin_users:
        print("No admin users found. Creating a new admin...")
        admin = User(
            email="admin@example.com",
            is_admin=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin user with email: admin@example.com and password: admin123")
    
    # If you want to reset an existing admin's password
    if admin_users and input("Reset admin password? (y/n): ").lower() == 'y':
        admin = admin_users[0]
        new_password = "admin123"  # You can change this to any password you want
        admin.password_hash = generate_password_hash(new_password)
        db.session.commit()
        print(f"Reset password for {admin.email} to: {new_password}")
