from getpass import getpass
from werkzeug.security import generate_password_hash

from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():

    username = input("Enter Admin username: ").strip()
    name = input("Enter Admin name: ").strip()
    password = getpass("Enter Admin password: ")
    confirm_password = getpass("Confirm password: ")

    if not username or not name or not password:
        print("All fields are required.")

    elif password != confirm_password:
        print("Passwords do not match.")

    elif User.query.filter_by(username=username).first():
        print("This username already exists.")

    else:
        admin = User(
            username=username,
            name=name,
            password=generate_password_hash(password),
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin account created successfully!")
        print("Username:", username)
        print("Role: Admin")