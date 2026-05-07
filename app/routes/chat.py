from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timezone
from app import db
from models import Conversation, Message
import uuid

chat = Blueprint("chat", __name__)

@chat.route("/conversation/start", methods=["POST"])
@login_required # app checks if user is signed in first and foremost
def start_conversation():
    data = request.json
    listing_id = data["listingID"]
    other_user_id = data["otherUserID"]

    # query checks if convos already exist, if not, make one
    convo = Conversation.query.filter(
        (
            (Conversation.user1_id == current_user.id) &
            (Conversation.user2_id == other_user_id)
        ) |
        (
            (Conversation.user1_id == other_user_id) &
            (Conversation.user2_id == current_user.id)
        )
    ).first()

    if not convo:
        convo = Conversation(
            listing_id=listing_id,
            user1_id=current_user.id,
            user2_id=other_user_id,
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(convo)
        db.session.commit()

    return jsonify({"conversation_id": convo.id})


@chat.route("/conversation/<int:conversation_id>/send", methods=["POST"])
@login_required
def send_message(conversation_id):
    data = request.json
    content = data.get("content")

    if not content:
        return jsonify({"error": "Message cannot be empty"}), 400
    
    conversation = Conversation.query.get_or_404(conversation_id)
    receiver_id = conversation.user2_id if conversation.user1_id == current_user.id else conversation.user1_id

    message = Message(
        id=str(uuid.uuid4())[:20], # gives the message a unique id to differentiate it
        sender_id=current_user.id,
        receiver_id=receiver_id,
        listing_id=conversation.listing_id,
        conversation_id=conversation_id,
        content=content,
        sent_at=datetime.now(timezone.utc)
    )

    db.session.add(message) # database adds/logs the message
    db.session.commit()

    return jsonify({"status": "sent"})


@chat.route("/conversation/<int:conversation_id>/messages", methods=["GET"])
@login_required
def get_messages(conversation_id):
    messages = Message.query.filter_by(conversation_id=conversation_id)\
                            .order_by(Message.sent_at.asc()).all() # order the messages by when it was sent 

    return jsonify([
        {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "content": msg.content,
            "sent_at": msg.sent_at.isoformat()
        }
        for msg in messages
    ])
