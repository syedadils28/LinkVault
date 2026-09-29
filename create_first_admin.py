import sys
from app import create_app, db
from app.models.user import User
import getpass

app = create_app()

with app.app_context():
    print("--- LinkVault Admin Creator ---")
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = getpass.getpass("Enter admin password: ")
    
    # Check if user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        print(f"Error: Username '{username}' already exists!")
        sys.exit(1)
        
    existing_email = User.query.filter_by(email=email).first()
    if existing_email:
        print(f"Error: Email '{email}' is already registered!")
        sys.exit(1)
        
    admin_user = User(username=username, email=email, is_admin=True)
    admin_user.set_password(password)
    
    db.session.add(admin_user)
    db.session.commit()
    
    print(f"\nSuccess! Administrator account '{username}' has been created.")
    print("You can now log in at /admin-login")
