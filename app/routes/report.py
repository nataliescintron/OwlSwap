from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from app import db
from models import User, Conversation, Report

report_bp = Blueprint("report", __name__)


@report_bp.route("/report/<int:conversation_id>/<reported_user_id>", methods=["GET", "POST"])
@login_required
def report_user(conversation_id, reported_user_id):

    reported_user = User.query.get_or_404(reported_user_id)
    conversation = Conversation.query.get_or_404(conversation_id)

    if request.method == "POST":

        reason = request.form.get("reason")
        description = request.form.get("description")

        report = Report(
            reporter_id=current_user.id,
            reported_user_id=reported_user.id,
            conversation_id=conversation.id,
            reason=reason,
            description=description
        )

        db.session.add(report)
        db.session.commit()

        return render_template("report_success.html")

    return render_template(
        "report.html",
        reported_user=reported_user,
        conversation=conversation
    )