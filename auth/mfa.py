"""TOTP-based multi-factor authentication routes."""

from __future__ import annotations

from datetime import datetime, timedelta
import secrets
import re
from flask import current_app, render_template, redirect, url_for, flash, session, request
from flask_login import login_required, current_user, login_user

from . import auth_bp
from .forms import TOTPSetupForm, TOTPVerifyForm, MFADisableForm, EmailCodeForm
from services.mfa import hash_code
from .totp import random_base32, provisioning_uri, verify_totp
from utils.mask import mask_email


@auth_bp.route("/mfa/setup", methods=["GET", "POST"])
@login_required
def mfa_setup():
    if current_user.mfa_enabled:
        flash("Two-step verification already enabled", "info")
        return redirect(url_for("index"))
    secret = session.get("mfa_secret")
    if not secret:
        secret = random_base32()
        session["mfa_secret"] = secret
    uri = provisioning_uri(secret, current_user.email, current_app.config.get("APP_NAME", "Heartlytics"))
    form = TOTPSetupForm()
    if form.validate_on_submit():
        code = re.sub(r"[^0-9A-Za-z]", "", form.code.data)
        if verify_totp(secret, code):
            current_user.set_mfa_secret(secret)
            codes = [secrets.token_hex(8) for _ in range(10)]
            current_user.mfa_recovery_hashes = [hash_code(c) for c in codes]
            current_user.mfa_enabled = True
            current_app.db.session.commit()
            session.pop("mfa_secret", None)
            session["recovery_codes"] = codes
            flash("Two-step verification enabled", "success")
            return redirect(url_for("auth.mfa_recovery_codes"))
        flash("Invalid code", "error")
    masked = f"{secret[:4]}••••{secret[-4:]}"
    return render_template("auth/mfa_setup.html", form=form, uri=uri, secret_masked=masked)


@auth_bp.route("/mfa/recovery", methods=["GET"])
@login_required
def mfa_recovery_codes():
    codes = session.get("recovery_codes")
    if not codes:
        return redirect(url_for("index"))
    return render_template("auth/mfa_recovery.html", codes=codes)


@auth_bp.route("/mfa/recovery/regenerate", methods=["POST"])
@login_required
def mfa_regenerate_codes():
    if not current_user.mfa_enabled:
        return redirect(url_for("index"))
    codes = [secrets.token_hex(8) for _ in range(10)]
    current_user.mfa_recovery_hashes = [hash_code(c) for c in codes]
    current_app.db.session.commit()
    session["recovery_codes"] = codes
    flash("Recovery codes regenerated", "success")
    return redirect(url_for("auth.mfa_recovery_codes"))


@auth_bp.route("/mfa/verify", methods=["GET", "POST"])
def mfa_verify():
    user_id = session.get("mfa_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    User = current_app.User
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("auth.login"))
    form = TOTPVerifyForm()
    if form.validate_on_submit():
        code = re.sub(r"[^0-9A-Za-z]", "", form.code.data)
        secret = user.mfa_secret
        if secret and verify_totp(secret, code):
            login_user(user)
            user.last_login = datetime.utcnow()
            user.mfa_last_enforced_at = datetime.utcnow()
            current_app.db.session.commit()
            session.pop("mfa_user_id", None)
            return redirect(request.args.get("next") or url_for("index"))
        hashed = hash_code(code)
        hashes = user.mfa_recovery_hashes or []
        if hashed in hashes:
            hashes.remove(hashed)
            user.mfa_recovery_hashes = hashes
            login_user(user)
            user.last_login = datetime.utcnow()
            user.mfa_last_enforced_at = datetime.utcnow()
            current_app.db.session.commit()
            session.pop("mfa_user_id", None)
            flash("Recovery code used", "warning")
            return redirect(url_for("index"))
        flash("Invalid code", "error")
    masked = mask_email(user.email)
    return render_template(
        "auth/mfa_verify.html",
        form=form,
        email_option=user.mfa_email_enabled,
        masked_email=masked,
    )


@auth_bp.route("/mfa/email", methods=["GET", "POST"])
def mfa_email():
    user_id = session.get("mfa_user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    User = current_app.User
    Challenge = current_app.MFAEmailChallenge
    user = User.query.get(user_id)
    if not user or not user.mfa_email_enabled:
        return redirect(url_for("auth.login"))
    form = EmailCodeForm()
    now = datetime.utcnow()
    challenge = (
        Challenge.query.filter_by(user_id=user.id, status="pending")
        .order_by(Challenge.id.desc())
        .first()
    )
    if request.method == "GET":
        send = True
        if challenge:
            cooldown = current_app.config.get("MFA_EMAIL_RESEND_COOLDOWN_SEC", 30)
            if (now - challenge.last_sent_at).total_seconds() < cooldown:
                send = False
        if send:
            length = current_app.config.get("MFA_EMAIL_CODE_LENGTH", 6)
            code = ''.join(secrets.choice('0123456789') for _ in range(length))
            hashed = hash_code(code)
            ttl = current_app.config.get("MFA_EMAIL_TTL_MIN", 10)
            if challenge:
                challenge.code_hash = hashed
                challenge.expires_at = now + timedelta(minutes=ttl)
                challenge.attempts = 0
                challenge.resend_count += 1
                challenge.last_sent_at = now
            else:
                challenge = Challenge(
                    user_id=user.id,
                    code_hash=hashed,
                    expires_at=now + timedelta(minutes=ttl),
                    last_sent_at=now,
                    requester_ip=request.remote_addr,
                    user_agent=request.headers.get("User-Agent", ""),
                )
                current_app.db.session.add(challenge)
            current_app.db.session.commit()
            text = f"Your verification code is {code}\nIt expires in {ttl} minutes."
            current_app.email_service.send_mail(
                user.email,
                "Your verification code",
                text,
                purpose="mfa.email",
            )
    if form.validate_on_submit():
        if not challenge or challenge.expires_at < now:
            flash("Code expired", "error")
        else:
            code = re.sub(r"[^0-9A-Za-z]", "", form.code.data)
            if hash_code(code) == challenge.code_hash:
                challenge.status = "verified"
                login_user(user)
                user.last_login = now
                user.mfa_last_enforced_at = now
                current_app.db.session.commit()
                session.pop("mfa_user_id", None)
                return redirect(request.args.get("next") or url_for("index"))
            challenge.attempts += 1
            current_app.db.session.commit()
            flash("Invalid code", "error")
    masked = mask_email(user.email)
    return render_template("auth/mfa_email.html", form=form, email=masked, challenge=challenge)


@auth_bp.route("/mfa/disable", methods=["GET", "POST"])
@login_required
def mfa_disable():
    if not current_user.mfa_enabled:
        return redirect(url_for("index"))
    form = MFADisableForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password.data):
            flash("Invalid password", "error")
        else:
            code = re.sub(r"[^0-9A-Za-z]", "", form.code.data)
            secret = current_user.mfa_secret
            valid = secret and verify_totp(secret, code)
            hashed = hash_code(code)
            hashes = current_user.mfa_recovery_hashes or []
            if not valid and hashed not in hashes:
                flash("Invalid code", "error")
            else:
                if hashed in hashes:
                    hashes.remove(hashed)
                    current_user.mfa_recovery_hashes = hashes
                current_user.mfa_enabled = False
                current_user.mfa_secret_ct = None
                current_user.mfa_secret_nonce = None
                current_user.mfa_secret_tag = None
                current_user.mfa_secret_wrapped_dk = None
                current_user.mfa_secret_kid = None
                current_user.mfa_secret_kver = None
                current_user.mfa_recovery_hashes = None
                current_app.db.session.commit()
                flash("Two-step verification disabled", "success")
                return redirect(url_for("index"))
    return render_template("auth/mfa_disable.html", form=form)


