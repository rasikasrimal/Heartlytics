from __future__ import annotations

import json
import os
from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from services.security import csrf_protect

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.get("/")
@login_required
def settings():
    """Display settings page with activity logs."""
    AuditLog = current_app.AuditLog
    logs = (
        AuditLog.query.filter_by(acting_user_id=current_user.id)
        .order_by(AuditLog.timestamp.desc())
        .limit(20)
        .all()
    )
    return render_template("settings.html", logs=logs)


@settings_bp.post("/profile")
@login_required
@csrf_protect
def update_profile():
    """Update basic user profile information."""
    db = current_app.db
    User = current_app.User
    current_user.username = request.form.get("username", current_user.username)
    current_user.email = request.form.get("email", current_user.email)
    nickname = request.form.get("nickname", "").strip() or None
    if nickname and db.session.query(User).filter(User.nickname == nickname, User.id != current_user.id).first():
        flash("Nickname already taken", "error")
        return redirect(url_for("settings.settings"))
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


@settings_bp.post("/password")
@login_required
@csrf_protect
def update_password():
    """Update the user's password after verifying current password."""
    db = current_app.db
    if current_user.check_password(request.form.get("current_password", "")):
        new_password = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")
        if new_password and new_password == confirm:
            current_user.set_password(new_password)
            db.session.commit()
            flash("Password updated", "success")
        else:
            flash("New passwords do not match", "error")
    else:
        flash("Incorrect current password", "error")
    return redirect(url_for("settings.settings"))


@settings_bp.post("/branding")
@login_required
@csrf_protect
def update_branding():
    """Allow SuperAdmins to update app name and logo."""
    if current_user.role != "SuperAdmin":
        abort(403)
    name = request.form.get("app_name", "").strip() or current_app.config.get("APP_NAME")
    logo_file = request.files.get("logo")
    if logo_file and logo_file.filename:
        ext = os.path.splitext(logo_file.filename)[1].lower()
        fname = f"logo{ext}"
        upload_path = os.path.join(current_app.static_folder, fname)
        logo_file.save(upload_path)
        current_app.config["APP_LOGO"] = fname
    current_app.config["APP_NAME"] = name
    branding_file = current_app.config.get("BRANDING_FILE")
    try:
        with open(branding_file, "w", encoding="utf-8") as f:
            json.dump({"app_name": current_app.config["APP_NAME"], "app_logo": current_app.config["APP_LOGO"]}, f)
    except Exception:
        pass
    flash("Branding updated", "success")
    return redirect(url_for("settings.settings"))
