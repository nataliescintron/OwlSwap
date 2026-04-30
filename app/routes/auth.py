from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for("marketplace"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Validation
        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "error")
            return redirect(url_for("auth.register"))

        if not email.endswith("@southernct.edu"):
            flash("Please use your @southernct.edu email.", "error")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("auth.register"))

        #Checks if user exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "error")
            return redirect(url_for("auth.register"))

        # Create user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Account created! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except Exception:
            db.session.rollback()
            flash("Registration failed. Try again.", "error")
            return redirect(url_for("auth.register"))

    # return render_template("register.html")
    #TODO ADD HTML
    return "<h1>Register Page (HTML template not connected yet)</h1>"


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for("marketplace"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for("auth.login"))

        # Check credentials
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get("remember_me") is not None)
            flash(f"Welcome back, {user.username}!", "success")
            return redirect(url_for("marketplace"))
        else:
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))

    # return render_template("login.html")
    # todo ADD HTML
    return "<h1>Login Page (HTML template not connected yet)</h1>"


@auth_bp.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))