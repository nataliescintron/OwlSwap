from dotenv import load_dotenv
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import uuid
import cloudinary

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///owlswap.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(user_id)

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.routes.chat import chat
    app.register_blueprint(chat, url_prefix="")

    from app.routes.delete_account import delete_bp
    app.register_blueprint(delete_bp)


    @app.route("/")
    def landing():
        return render_template("landing.html")

    @app.route("/marketplace")
    @login_required
    def marketplace():
        from models import Listing, User
        listings = Listing.query.filter_by(is_available=True).all()
        total = Listing.query.count()
        available = Listing.query.filter_by(is_available=True).count()
        users = User.query.count()
        return render_template("marketplace.html", listings=listings,
                               total_listings=total,
                               available_listings=available,
                               total_users=users)

    @app.route("/listing/<listing_id>")
    @login_required
    def listing_detail(listing_id):
        from models import Listing
        listing = Listing.query.get_or_404(listing_id)
        related = []
        if listing.course:
            related = Listing.query.filter(
                Listing.course == listing.course,
                Listing.id != listing.id,
                Listing.is_available == True
            ).limit(4).all()
        return render_template("listing_detail.html", listing=listing, related=related)

    @app.route("/listing/new", methods=["GET", "POST"])
    @login_required
    def create_listing_page():
        from models import Listing, Book, ListingImage
        import cloudinary.uploader
        if request.method == "POST":
            isbn      = request.form.get("isbn", "").strip()
            title     = request.form.get("title", "").strip()
            author    = request.form.get("author", "").strip()
            edition   = request.form.get("edition", "").strip()
            year      = request.form.get("year", "").strip()
            condition = request.form.get("condition", "").strip()
            price     = request.form.get("price", "").strip()
            course    = request.form.get("course", "").strip()
            image     = request.files.get("image")

            if not title or not condition:
                flash("Title and condition are required.", "error")
                return redirect(url_for("create_listing_page"))

            if not isbn:
                isbn = str(uuid.uuid4())[:20]

            try:
                book = Book.query.get(isbn)
                if not book:
                    book = Book(
                        isbn=isbn,
                        title=title,
                        author=author if author else "Unknown",
                        edition=edition,
                        year=int(year) if year else None
                    )
                    db.session.add(book)

                listing = Listing(
                    id=str(uuid.uuid4())[:20],
                    user_id=current_user.id,
                    book_isbn=isbn,
                    condition=condition,
                    price=float(price) if price else None,
                    course=course,
                    is_available=True
                )
                db.session.add(listing)
                db.session.flush()

                if image and image.filename != "":
                    upload_result = cloudinary.uploader.upload(image)
                    listing_image = ListingImage(
                        id=str(uuid.uuid4())[:20],
                        listing_id=listing.id,
                        image_url=upload_result["secure_url"]
                    )
                    db.session.add(listing_image)

                db.session.commit()
                flash("Listing created successfully!", "success")
                return redirect(url_for("marketplace"))
            except Exception as e:
                db.session.rollback()
                flash(f"Failed to create listing: {e}", "error")
                return redirect(url_for("create_listing_page"))

        return render_template("create_listing.html")

    @app.route("/my-listings")
    @login_required
    def my_listings():
        from models import Listing
        listings = Listing.query.filter_by(user_id=current_user.id).all()
        return render_template("my_listings.html", listings=listings)

    @app.route("/listing/<listing_id>/complete", methods=["POST"])
    @login_required
    def complete_listing(listing_id):
        from models import Listing
        listing = Listing.query.get_or_404(listing_id)
        if listing.user_id == current_user.id:
            listing.is_available = False
            db.session.commit()
            flash("Listing marked as completed.", "success")
        return redirect(url_for("my_listings"))

    @app.route("/messages")
    @login_required
    def messages_page():
        from models import Conversation
        conversations = Conversation.query.filter(
            (Conversation.user1_id == current_user.id) |
            (Conversation.user2_id == current_user.id)
        ).all()
        return render_template("messages.html", conversations=conversations)

    @app.route("/profile")
    @login_required
    def profile_page():
        from models import Listing
        listings = Listing.query.filter_by(user_id=current_user.id).all()
        total = len(listings)
        active = len([l for l in listings if l.is_available])
        completed = len([l for l in listings if not l.is_available])
        return render_template("profile.html", user=current_user,
                               listings=listings,
                               total_listings=total,
                               active_listings=active,
                               completed_listings=completed)


    @app.route("/listing/<listing_id>/delete", methods=["POST"])
    @login_required
    def delete_listing(listing_id):
        from models import Listing
        listing = Listing.query.get_or_404(listing_id)
        if listing.user_id == current_user.id:
            db.session.delete(listing)
            db.session.commit()
            flash("Listing deleted.", "success")
        return redirect(url_for("my_listings"))

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    with app.app_context():
        db.create_all()

    return app
