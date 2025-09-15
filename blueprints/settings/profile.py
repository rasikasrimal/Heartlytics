from __future__ import annotations

import json
import os
from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash, abort, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from services.security import csrf_protect

settings_bp = Blueprint("settings", __name__, url_prefix="/settings")


@settings_bp.get("/")
@login_required
def settings():
    """Display settings page with activity logs."""
    AuditLog = current_app.AuditLog
    # Compute next allowed username change date (30-day cooldown)
    next_change_at = None
    cooldown_active = False
    if getattr(current_user, "last_username_change_at", None):
        next_change_at = current_user.last_username_change_at + timedelta(days=30)
        try:
            cooldown_active = next_change_at > datetime.utcnow()
        except Exception:
            cooldown_active = False
    # Pull any cooldown flag set by POST handler to trigger modal
    cooldown_until = session.pop("username_cooldown_until", None)
    logs = (
        AuditLog.query.filter_by(acting_user_id=current_user.id)
        .order_by(AuditLog.timestamp.desc())
        .limit(20)
        .all()
    )
    return render_template(
        "settings/index.html",
        logs=logs,
        username_next_change_at=next_change_at,
        username_cooldown_active=cooldown_active,
        username_cooldown_until=cooldown_until,
        username_hold_days=20,
    )


@settings_bp.post("/profile")
@login_required
@csrf_protect
def update_profile():
    """Update basic user profile information."""
    db = current_app.db
    User = current_app.User
    UsernameReservation = current_app.UsernameReservation
    AuditLog = current_app.AuditLog

    new_username = (request.form.get("username", current_user.username) or "").strip()
    new_email = request.form.get("email", current_user.email)

    # Enforce username change policy
    if new_username and new_username != current_user.username:
        # 30-day cooldown check
        now = datetime.utcnow()
        if current_user.last_username_change_at and now < current_user.last_username_change_at + timedelta(days=30):
            next_at = current_user.last_username_change_at + timedelta(days=30)
            # Persist until timestamp for UI modal
            session["username_cooldown_until"] = next_at.isoformat()
            flash("You can change your username again later.", "warning")
            return redirect(url_for("settings.settings"))

        # Uniqueness against other users
        exists = db.session.query(User).filter(User.username == new_username, User.id != current_user.id).first()
        if exists:
            flash("Username already taken", "error")
            return redirect(url_for("settings.settings"))

        # Check reservation hold by another user
        res = (
            UsernameReservation.query.filter_by(username=new_username)
            .filter(UsernameReservation.reserved_until >= datetime.utcnow())
            .first()
        )
        if res and res.user_id != current_user.id:
            flash("That username is reserved right now. Please choose another.", "error")
            return redirect(url_for("settings.settings"))

        # Create reservation for the old username for 20 days
        old_username = current_user.username
        hold_until = now + timedelta(days=20)
        existing_res = UsernameReservation.query.filter_by(username=old_username).first()
        if existing_res:
            existing_res.reserved_until = hold_until
            existing_res.user_id = current_user.id
        else:
            db.session.add(
                UsernameReservation(
                    username=old_username,
                    reserved_until=hold_until,
                    user_id=current_user.id,
                )
            )

        # Apply username change and record timestamp
        current_user.username = new_username
        current_user.last_username_change_at = now
        # Audit log
        db.session.add(
            AuditLog(
                acting_user_id=current_user.id,
                target_user_id=current_user.id,
                action="username_change",
                old_value=old_username,
                new_value=new_username,
            )
        )

    # Update email and other fields
    current_user.email = new_email
    raw_nick = request.form.get("nickname", "").strip()
    nickname = raw_nick or None
    if raw_nick.lower() == "none":
        nickname = None
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
