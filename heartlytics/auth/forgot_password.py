"""Forgot password flow: issue, verify and reset passwords via codes."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

from flask import current_app, render_template, request, session, redirect, url_for, flash
import re
from sqlalchemy import or_

from ..services import mfa

from . import auth_bp
from .forms import ForgotPasswordForm, VerifyCodeForm, ResetPasswordForm


def _mask_email(email: str) -> str:
    try:
        local, domain = email.split("@")
    except ValueError:
        return email
    if len(local) <= 2:
        return local[0] + "*" * (len(local) - 1) + "@" + domain
    return f"{local[0]}••••{local[-1]}@{domain}"

def _rate_limited(key: str, limit: int) -> bool:
    rl = session.setdefault("rate_limits", {})
    data = rl.get(key)
    now = datetime.utcnow()
    if data and now - datetime.fromisoformat(data["ts"]) < timedelta(hours=1):
        if data["count"] >= limit:
            return True
        data["count"] += 1
    else:
        rl[key] = {"count": 1, "ts": now.isoformat()}
    session["rate_limits"] = rl
    return False

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
        per_ip = current_app.config.get("RATE_LIMIT_PER_IP", 5)
        per_id = current_app.config.get("RATE_LIMIT_PER_ID", 5)
        if _rate_limited(f"ip:{request.remote_addr}", per_ip) or _rate_limited(
            f"id:{ident}", per_id
        ):
            current_app.logger.warning(
                "otp.resend.blocked ident=%s ip=%s", ident, request.remote_addr
            )
            flash(
                "If an account is associated with the details you provided, a verification code has been sent to the registered email.",
                "info",
            )
            return redirect(url_for("auth.verify_forgot"))

        db = current_app.db
        User = current_app.User
        PasswordResetRequest = current_app.PasswordResetRequest
        user = User.query.filter(or_(User.email == ident, User.username == ident)).first()
        request_id = str(uuid.uuid4())
        if user:
            code = mfa.generate_code()
            hashed = mfa.hash_code(code)
            now = datetime.utcnow()
            ttl = current_app.config.get("OTP_TTL_MIN", 10)
            pr = PasswordResetRequest(
                request_id=request_id,
                user_id=user.id,
                hashed_code=hashed,
                expires_at=now + timedelta(minutes=ttl),
                last_sent_at=now,
                requester_ip=request.remote_addr,
                user_agent=request.headers.get("User-Agent"),
            )
            db.session.add(pr)
            db.session.commit()
            mfa.send_reset_email(user, code, ttl, request)
            current_app.logger.info(
                "otp.issued user=%s request=%s", _mask_email(user.email), request_id
            )
            session["pr_id"] = request_id
        else:
            session.pop("pr_id", None)
        flash(
            "If an account is associated with the details you provided, a verification code has been sent to the registered email.",
            "info",
        )
        return redirect(url_for("auth.verify_forgot"))
    return render_template("auth/forgot.html", form=form)


@auth_bp.route("/forgot/verify", methods=["GET", "POST"])
def verify_forgot():
    pr = _get_request()
    form = VerifyCodeForm()
    if form.validate_on_submit() and pr:
        if datetime.utcnow() > pr.expires_at:
            current_app.logger.info(
                "otp.expired user=%s request=%s", _mask_email(pr.user.email), pr.request_id
            )
            flash("Code expired. Request a new code.", "error")
            return redirect(url_for("auth.forgot"))
        max_attempts = current_app.config.get("OTP_MAX_ATTEMPTS", 5)
        if pr.attempts >= max_attempts:
            current_app.logger.warning(
                "otp.failed attempts_exhausted user=%s request=%s", _mask_email(pr.user.email), pr.request_id
            )
            flash("Too many attempts. Request a new code.", "error")
            return redirect(url_for("auth.forgot"))
        pr.attempts += 1
        code = re.sub(r"[^0-9A-Za-z]", "", form.code.data)
        if mfa.verify_code(code, pr.hashed_code):
            pr.status = "verified"
            current_app.db.session.commit()
            session["pr_verified"] = True
            current_app.logger.info(
                "otp.verified user=%s request=%s", _mask_email(pr.user.email), pr.request_id
            )
            return redirect(url_for("auth.reset_password"))
        current_app.db.session.commit()
        remaining = max_attempts - pr.attempts
        current_app.logger.warning(
            "otp.failed user=%s request=%s remaining=%s",
            _mask_email(pr.user.email),
            pr.request_id,
            remaining,
        )
        flash(f"Invalid code. You have {remaining} attempts remaining.", "error")
    cooldown = current_app.config.get("OTP_RESEND_COOLDOWN_SEC", 30)
    remaining = 0
    masked = ""
    if pr:
        elapsed = (datetime.utcnow() - pr.last_sent_at).total_seconds()
        if elapsed < cooldown:
            remaining = int(cooldown - elapsed)
        masked = _mask_email(pr.user.email)
    return render_template("auth/verify.html", form=form, cooldown=remaining, masked_email=masked)


@auth_bp.route("/forgot/resend", methods=["POST"])
def resend_code():
    pr = _get_request()
    if not pr:
        flash("Request a new code.", "error")
        return redirect(url_for("auth.forgot"))
    now = datetime.utcnow()
    cooldown = current_app.config.get("OTP_RESEND_COOLDOWN_SEC", 30)
    if (now - pr.last_sent_at).total_seconds() < cooldown:
        current_app.logger.warning(
            "otp.resend.blocked cooldown user=%s request=%s",
            _mask_email(pr.user.email),
            pr.request_id,
        )
        flash("Please wait before requesting a new code.", "error")
        return redirect(url_for("auth.verify_forgot"))
    if pr.resend_count >= 10:
        current_app.logger.warning(
            "otp.resend.blocked daily user=%s request=%s",
            _mask_email(pr.user.email),
            pr.request_id,
        )
        flash("Daily limit reached. Try again later.", "error")
        return redirect(url_for("auth.verify_forgot"))
    code = mfa.generate_code()
    pr.hashed_code = mfa.hash_code(code)
    ttl = current_app.config.get("OTP_TTL_MIN", 10)
    pr.expires_at = now + timedelta(minutes=ttl)
    pr.resend_count += 1
    pr.last_sent_at = now
    current_app.db.session.commit()
    mfa.send_reset_email(pr.user, code, ttl, request)
    current_app.logger.info(
        "otp.issued user=%s request=%s", _mask_email(pr.user.email), pr.request_id
    )
    flash(
        "If an account is associated with the details you provided, a verification code has been sent to the registered email.",
        "info",
    )
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
        current_app.email_service.send_mail(
            user.email,
            "Your password was changed",
            "If you did not initiate this change, please contact support immediately.",
            "If you did not initiate this change, please contact support immediately.",
            purpose="security",
        )
        if current_app.config.get("AUTO_LOGIN_AFTER_RESET"):
            from flask_login import login_user

            login_user(user)
            return redirect(url_for("index"))
        return redirect(url_for("auth.login", identifier=user.email))
    return render_template("auth/reset.html", form=form)
