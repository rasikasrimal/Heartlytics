from __future__ import annotations

import os
from flask import (
    Blueprint,
    current_app,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
)
from flask_login import login_required, current_user
from services.security import csrf_protect, csrf_protect_api

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.route("/", methods=["GET", "POST"])
@login_required
@csrf_protect
def settings():
    """Display and update profile, password, and activity logs."""
    db = current_app.db
    AuditLog = current_app.AuditLog
    User = current_app.User

    if request.method == "POST":
        if "current_password" in request.form:
            if current_user.check_password(request.form.get("current_password", "")):
                current_user.set_password(request.form.get("new_password", ""))
                db.session.commit()
                flash("Password updated", "success")
            else:
                flash("Incorrect current password", "error")
        else:
            current_user.username = request.form.get("username", current_user.username)
            current_user.email = request.form.get("email", current_user.email)
            nickname = request.form.get("nickname", "").strip() or None
            current_user.bio = request.form.get("bio", current_user.bio)
            if nickname and db.session.query(User).filter(User.nickname == nickname, User.id != current_user.id).first():
                flash("Nickname already taken", "error")
            else:
                current_user.nickname = nickname
            avatar_file = request.files.get("avatar")
            if avatar_file and avatar_file.filename:
                ext = os.path.splitext(avatar_file.filename)[1].lower()
                if ext.lstrip(".") in current_app.config.get("ALLOWED_AVATAR_EXTENSIONS", set()):
                    fname = f"{current_user.uid}{ext}"
                    path = os.path.join(current_app.config["AVATAR_UPLOAD_FOLDER"], fname)
                    avatar_file.save(path)
                    current_user.avatar = fname
            db.session.commit()
            flash("Profile updated", "success")
        return redirect(url_for("settings.settings"))

    logs = (
        AuditLog.query.filter_by(acting_user_id=current_user.id)
        .order_by(AuditLog.timestamp.desc())
        .limit(20)
        .all()
    )
    return render_template("settings.html", logs=logs)


@settings_bp.post("/verify_password")
@login_required
@csrf_protect_api
def verify_password():
    """AJAX endpoint to validate the user's current password."""
    data = request.get_json(silent=True) or {}
    valid = current_user.check_password(data.get("password", ""))
    return jsonify({"valid": valid})
