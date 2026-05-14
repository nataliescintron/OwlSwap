from datetime import datetime, timezone
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.String(20), primary_key=True)
    f_name = db.Column(db.String(15), nullable=False)
    l_name = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    book_interests = db.Column(db.Text, nullable=True)   
    rating = db.Column(db.Numeric(3, 2), nullable=True)  
    rating_count = db.Column(db.Integer, default=0) 
    is_deleted = db.Column(db.Boolean, default=False)


    listings = db.relationship(
        "Listing", backref="owner", lazy=True, cascade="all, delete-orphan"
    )
    messages_sent = db.relationship(
        "Message", foreign_keys="Message.sender_id",
        backref="sender", lazy=True, cascade="all, delete-orphan"
    )
    messages_received = db.relationship(
        "Message", foreign_keys="Message.receiver_id",
        backref="receiver", lazy=True, cascade="all, delete-orphan"
    )
    reviews_written = db.relationship(
    "Review",
    foreign_keys="Review.reviewer_id",
    backref="review_author",
    lazy=True)
    
    @property
    def average_rating(self):
        reviews = self.reviews_received

        if not reviews:
            return None

        return round(
            sum(r.rating for r in reviews) / len(reviews),
            1
        )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


class Book(db.Model):
    __tablename__ = "books"

    isbn = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    edition = db.Column(db.String(50))
    year = db.Column(db.Integer)
    image_url = db.Column(db.Text)

    listings = db.relationship("Listing", backref="book", lazy=True)


class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey("users.id"), nullable=False)
    book_isbn = db.Column(db.String(20), db.ForeignKey("books.isbn"), nullable=False)

    genre = db.Column(db.String(50), nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    condition = db.Column(db.String(20),nullable=False)
    course = db.Column(db.String(10), nullable=True)  

    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    messages = db.relationship(
        "Message", backref="listing", lazy=True, cascade="all, delete-orphan"
    )
    images = db.relationship(
        "ListingImage", backref="listing", lazy=True, cascade="all, delete-orphan"
    )


class ListingImage(db.Model):
    __tablename__ = "listing_images"

    id = db.Column(db.String(20), primary_key=True)
    listing_id = db.Column(db.String(20), db.ForeignKey("listings.id"), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.String(20), primary_key=True)
    sender_id = db.Column(db.String(20), db.ForeignKey("users.id"), nullable=False)
    listing_id = db.Column(db.String(20), db.ForeignKey("listings.id"), nullable=False)
    receiver_id = db.Column(db.String(20), db.ForeignKey("users.id"), nullable=False)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"))
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.String(20), db.ForeignKey("listings.id"))
    user1_id = db.Column(db.String(20), db.ForeignKey("users.id"))
    user2_id = db.Column(db.String(20), db.ForeignKey("users.id"))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    #to get conversation working
    user1 = db.relationship("User", foreign_keys=[user1_id], backref="conversations_as_user1")
    user2 = db.relationship("User", foreign_keys=[user2_id], backref="conversations_as_user2")
    listing = db.relationship("Listing", backref="conversations")

class Review(db.Model):
    __tablename__ = "reviews"

    id = db.Column(db.String(20), primary_key=True)
    reviewer_id = db.Column(
        db.String(20),
        db.ForeignKey("users.id"),
        nullable=False
    )
    reviewed_user_id = db.Column(
        db.String(20),
        db.ForeignKey("users.id"),
        nullable=False
    )
    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversations.id"),
        nullable=False
    )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=True)

    # buyer or seller
    role = db.Column(db.String(10), nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewer_id]
    )
    reviewed_user = db.relationship(
        "User",
        foreign_keys=[reviewed_user_id],
        backref="reviews_received"
    )