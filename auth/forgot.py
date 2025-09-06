"""Forgot password flow: issue, verify and reset passwords via codes."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
import secrets
import hashlib

from flask import current_app, render_template, request, session, redirect, url_for, flash
from sqlalchemy import or_

from . import auth_bp
from .forms import ForgotPasswordForm, VerifyCodeForm, ResetPasswordForm


def _generate_code() -> str:
    return f"{secrets.randbelow(10**6):06d}"


def _hash_code(code: str) -> str:
    pepper = current_app.config.get("OTP_PEPPER", "")
    return hashlib.sha256((pepper + code).encode()).hexdigest()


def _get_request() -> 'PasswordResetRequest | None':
    request_id = session.get("pr_id")
    if not request_id:
        return None
    PasswordResetRequest = current_app.PasswordResetRequest
    return PasswordResetRequest.query.filter_by(request_id=request_id).first()


@auth_bp.route("/forgot", methods=["GET", "POST"])
def forgot():
    """Step 1: collect identifier and issue verification code."""
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        ident = form.identifier.data.strip()
        db = current_app.db
        User = current_app.User
        PasswordResetRequest = current_app.PasswordResetRequest
        user = User.query.filter(or_(User.email == ident, User.username == ident)).first()
        request_id = str(uuid.uuid4())
        if user:
            code = _generate_code()
            hashed = _hash_code(code)
            now = datetime.utcnow()
            pr = PasswordResetRequest(
                request_id=request_id,
                user_id=user.id,
                hashed_code=hashed,
                expires_at=now + timedelta(minutes=10),
                last_sent_at=now,
                requester_ip=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
            )
            db.session.add(pr)
            db.session.commit()
            current_app.logger.info(f"Password reset code for {user.email}: {code}")
            session["pr_id"] = request_id
        else:
            session.pop("pr_id", None)
        flash("If an account is associated with the details you provided, a verification code has been sent to the registered email.", "info")
        return redirect(url_for("auth.verify_forgot"))
    return render_template("auth/forgot.html", form=form)


@auth_bp.route("/forgot/verify", methods=["GET", "POST"])
def verify_forgot():
    pr = _get_request()
    form = VerifyCodeForm()
    if form.validate_on_submit() and pr:
        if datetime.utcnow() > pr.expires_at:
            flash("Code expired. Request a new code.", "error")
            return redirect(url_for("auth.forgot"))
        if pr.attempts >= 5:
            flash("Too many attempts. Request a new code.", "error")
            return redirect(url_for("auth.forgot"))
        pr.attempts += 1
        if _hash_code(form.code.data.strip()) == pr.hashed_code:
            pr.status = "verified"
            current_app.db.session.commit()
            session["pr_verified"] = True
            return redirect(url_for("auth.reset_password"))
        current_app.db.session.commit()
        remaining = 5 - pr.attempts
        flash(f"Invalid code. You have {remaining} attempts remaining.", "error")
    return render_template("auth/verify.html", form=form)


@auth_bp.route("/forgot/resend", methods=["POST"])
def resend_code():
    pr = _get_request()
    if not pr:
        flash("Request a new code.", "error")
        return redirect(url_for("auth.forgot"))
    now = datetime.utcnow()
    if (now - pr.last_sent_at).total_seconds() < 30:
        flash("Please wait before requesting a new code.", "error")
        return redirect(url_for("auth.verify_forgot"))
    if pr.resend_count >= 10:
        flash("Daily limit reached. Try again later.", "error")
        return redirect(url_for("auth.verify_forgot"))
    code = _generate_code()
    pr.hashed_code = _hash_code(code)
    pr.expires_at = now + timedelta(minutes=10)
    pr.resend_count += 1
    pr.last_sent_at = now
    current_app.db.session.commit()
    current_app.logger.info(f"Password reset code resend for user {pr.user_id}: {code}")
    flash("If an account is associated with the details you provided, a verification code has been sent to the registered email.", "info")
    return redirect(url_for("auth.verify_forgot"))


@auth_bp.route("/forgot/reset", methods=["GET", "POST"])
def reset_password():
    pr = _get_request()
    if not pr or not session.get("pr_verified"):
        return redirect(url_for("auth.forgot"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = pr.user
        if not user:
            flash("Request a new code.", "error")
            return redirect(url_for("auth.forgot"))
        user.set_password(form.password.data)
        pr.status = "used"
        current_app.db.session.commit()
        session.pop("pr_id", None)
        session.pop("pr_verified", None)
        flash("Password updated", "success")
        from flask_login import login_user

        login_user(user)
        return redirect(url_for("index"))
    return render_template("auth/reset.html", form=form)
