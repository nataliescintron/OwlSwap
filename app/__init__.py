from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


load_dotenv()

from flask import Flask, render_template
from flask_login import LoginManager, login_required

import os

login_manager = LoginManager()


def create_app():
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)

    # Configuration
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "sqlite:///owlswap.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    # Load logged-in user from session
    @login_manager.user_loader
    def load_user(user_id):
        from models import User

        #TODO: is userid a string or integer?

        return User.query.get(user_id)

    # Register blueprints
    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # Main routes
    @app.route("/")
    def landing():
        return render_template("landing.html")
        # TODO: HTML NAMING CHECK

    @app.route("/marketplace")
    @login_required
    def marketplace():
        return render_template("marketplace.html")
    # TODO: HTML NAMING CHECK

    # Create database tables
    with app.app_context():
        db.create_all()

    return app