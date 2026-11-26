from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import check_password_hash, generate_password_hash

from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()

        if user and user.password:

            stored_password = user.password

            # Check whether the password is already hashed
            if stored_password.startswith(("pbkdf2:", "scrypt:")):
                password_valid = check_password_hash(
                    stored_password, password
                )
            else:
                # Support existing demo users with plain-text passwords
                password_valid = stored_password == password

                # Upgrade old password to a secure hash after successful login
                if password_valid:
                    user.password = generate_password_hash(password)
                    from app import db
                    db.session.commit()

            if password_valid:

                session.clear()

                session["user_id"] = user.id
                session["username"] = user.username
                session["role"] = user.role
                session["name"] = user.name

                flash("Login successful!", "success")

                return redirect(url_for("dashboard.main_dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.", "success")

    return redirect(url_for("auth.login"))