from flask import Blueprint, request, jsonify
from app import db
from app.models import Listing, Book, User
from flask_login import login_required, current_user

listings_bp = Blueprint("listings", __name__)

#Create a Listing
@listings_bp.route("/", methods=["POST"])
@login_required
def create_listing():
    data = request.json

    listing = Listing(
        id=data["id"],
        user_id=current_user.id,  
        book_isbn=data["book_isbn"],
        condition=data.get("condition"),
        price=data.get("price"),
        is_available=True
    )

    db.session.add(listing)
    db.session.commit()

    return jsonify({"message": "Listing created"}), 201

#get all listing aka all listing will pop up
@listings_bp.route("/", methods=["GET"])
def get_listings():
    listings = Listing.query.filter_by(is_available=True).all()

    return jsonify([
        {
            "id": l.id,
            "book_title": l.book.title if l.book else None,
            "author": l.book.author if l.book else None,
            "price": str(l.price) if l.price else None,
            "condition": l.condition,
            "owner": l.owner.f_name if l.owner else None,
            "images": [img.image_url for img in l.images]
        }
        for l in listings
    ]), 200

# Mark listing as completed
@listings_bp.route("/<listing_id>/complete", methods=["POST"])
@login_required
def complete_listing(listing_id):
    listing = Listing.query.get(listing_id)

    if not listing:
        return jsonify({"error": "Listing not found"}), 404

    # only owner can mark as completed
    if listing.user_id != current_user.id:
        return jsonify({"error": "Not authorized"}), 403

    listing.is_available = False  

    db.session.commit()

    return jsonify({"message": "Listing marked as completed"}), 200
