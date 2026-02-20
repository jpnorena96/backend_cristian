from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    email = "admin@legaltech.com"
    password = "admin" # In real app, hash this!
    
    user = User.query.filter_by(email=email).first()
    if user:
        print(f"User {email} already exists. Updating to admin...")
        user.is_admin = True
        user.password_hash = password # Reset pass for easy testing
        user.role = 'admin'
    else:
        print(f"Creating new admin user {email}...")
        user = User(
            email=email,
            password_hash=password,
            full_name="Super Admin",
            role='admin',
            is_admin=True
        )
        db.session.add(user)
    
    db.session.commit()
    print("Admin user ready. Login with:")
    print(f"Email: {email}")
    print(f"Password: {password}")
