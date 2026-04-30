from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

#user entity
class User(db.Model):
    __tablename__ = "users"
    #attributes
    id = db.Column(db.String(20), primary_key = True)
    f_name = db.Column(db.String(15),nullable = False)
    l_name = db.Column(db.String(15),nullable = False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #relationships
    listings = db.relationship(
        "Listing",
        backref = "owner",
        lazy = True,
        cascade = "all, delete-orphan"
    )
    #messages sent by user (1 to many)
    messages_sent = db.relationship(
        "Message",
        foreign_keys ="Message.sender_id",
        backref="sender",
        lazy = True,
        cascade = "all, delete-orphan"
    )

    # Messages received by user (1 to many)
    messages_received = db.relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        backref="receiver",
        lazy=True,
        cascade="all, delete-orphan"
    )

#book entity
class Book(db.Model):
    __tablename__ = "books"

    isbn = db.Column(db.String(20), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255))
    edition = db.Column(db.String(50))
    year = db.Column(db.Integer(4))
    image_url = db.Column(db.Text)
    #relationship
    listings = db.relationship("Listing", backref="book", lazy=True)

#Listing entity
class Listing(db.Model):
    __tablename__ = "listings"

    id = db.Column(db.String(20), primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey("users.id"), nullable=False)
    book_isbn = db.Column(db.String(20), db.ForeignKey("books.isbn"), nullable=False)
    condition = db.Column(db.String(50)) #"new", "good", "fair"
    price = db.Column(db.Numeric(10, 2), nullable=True)
    is_available = db.Column(db.Boolean, default=True) #this is the equivalent of status on the ER diagram

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # Relationships
    messages = db.relationship(
        "Message",
        backref="listing",
        lazy=True,
        cascade="all, delete-orphan"
    )
    images = db.relationship(
        "ListingImage",
        backref="listing",
        lazy=True,
        cascade="all, delete-orphan"
    )
#images for listing
class ListingImage(db.Model):
    __tablename__ = "listing_images"
    id = db.Column(db.String(20), primary_key=True)
    listing_id = db.Column(db.String(20), db.ForeignKey("listings.id"), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
#messages? could change for contact session type chat

class Message(db.Model):
    __tablename__ = "messages"
    id = db.Column(db.String(20), primary_key=True)
    sender_id = db.Column(db.String(20), db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.String(20), db.ForeignKey("users.id"), nullable=False)
    listing_id = db.Column(db.String(20), db.ForeignKey("listings.id"))
    content = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))



