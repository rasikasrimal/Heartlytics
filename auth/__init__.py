"""Authentication blueprint handling user login, sign-up and logout."""

from __future__ import annotations

from datetime import datetime, timedelta

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    session,
    url_for,
    request,
)
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_

from .forms import LoginForm, SignupForm, EmailCodeForm
from services import mfa as mfa_service


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _too_many_attempts() -> bool:
    """Simple rate limiter: allow 5 attempts per 15 minutes."""
    data = session.get("login_attempts")
    if not data:
        return False
    count = data.get("count", 0)
    ts = datetime.fromisoformat(data.get("ts"))
    if count >= 5 and datetime.utcnow() - ts < timedelta(minutes=15):
        return True
    if datetime.utcnow() - ts >= timedelta(minutes=15):
        session["login_attempts"] = {"count": 0, "ts": datetime.utcnow().isoformat()}
    return False


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate a user and start a session."""

    form = LoginForm()
    if request.method == "GET" and request.args.get("identifier"):
        form.identifier.data = request.args.get("identifier")
    if form.validate_on_submit():
        if _too_many_attempts():
            flash("Too many login attempts. Please try again later.", "error")
            return render_template("auth/login.html", form=form)

        db = current_app.db
        User = current_app.User
        ident = form.identifier.data.strip()
        user = User.query.filter(
            or_(User.email == ident, User.username == ident)
        ).first()

        if user and user.check_password(form.password.data):
            if not user.email_verified_at:
                flash("Please verify your email before logging in.", "error")
                return render_template("auth/login.html", form=form)
            if user.status != "approved":
                if user.status == "pending":
                    msg = "Account pending approval"
                elif user.status == "suspended":
                    msg = "Account suspended"
                else:
                    msg = "Account rejected"
                flash(msg, "error")
                return render_template("auth/login.html", form=form)

            if not user.mfa_email_enabled:
                user.mfa_email_enabled = True
                user.mfa_email_verified_at = datetime.utcnow()
                db.session.commit()

            if user.mfa_enabled:
                session["mfa_user_id"] = user.id
                session["login_attempts"] = {"count": 0, "ts": datetime.utcnow().isoformat()}
                return redirect(url_for("auth.mfa_verify"))
            login_user(user)
            user.last_login = datetime.utcnow()
            db.session.commit()
            session["login_attempts"] = {"count": 0, "ts": datetime.utcnow().isoformat()}
            session.permanent = True  # enable session timeout
            if user.role == "SuperAdmin":
                return redirect(url_for("superadmin.dashboard"))
            if user.role == "Admin":
                return redirect(url_for("superadmin.dashboard"))
            if user.role == "Doctor":
                return redirect(url_for("dashboard"))
            return redirect(url_for("index"))

        data = session.get("login_attempts") or {"count": 0, "ts": datetime.utcnow().isoformat()}
        data["count"] += 1
        session["login_attempts"] = data
        flash("Invalid credentials", "error")

    # Clear sensitive fields so the form always renders blank
    form.identifier.data = ""
    form.password.data = ""
    return render_template("auth/login.html", form=form)


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Register a new user. Users activate immediately; Doctors/Admins await approval."""

    form = SignupForm()
    # Limit role choices for public signups to non-superadmin roles.
    if not (current_user.is_authenticated and current_user.role == "SuperAdmin"):
        form.role.choices = [("User", "User"), ("Doctor", "Doctor"), ("Admin", "Admin")]

    if form.validate_on_submit():
        db = current_app.db
        User = current_app.User

        # Prevent duplicate usernames/emails.
        if User.query.filter(
            or_(User.username == form.username.data, User.email == form.email.data)
        ).first():
            flash("Username or email already exists", "error")
            return render_template("auth/signup.html", form=form)
        if form.nickname.data and User.query.filter_by(nickname=form.nickname.data).first():
            flash("Nickname already exists", "error")
            return render_template("auth/signup.html", form=form)

        if current_user.is_authenticated and current_user.role == "SuperAdmin":
            role = form.role.data
            status = "approved"
            requested_role = None
        else:
            requested_role = form.role.data if form.role.data != "User" else None
            role = "User"
            status = "approved" if requested_role is None else "pending"

        user = User(
            username=form.username.data,
            nickname=form.nickname.data or None,
            email=form.email.data,
            role=role,
            status=status,
            requested_role=requested_role,
            created_at=datetime.utcnow(),
        )
        user.set_password(form.password.data)

        if current_user.is_authenticated and current_user.role == "SuperAdmin":
            # Superadmin-created accounts skip email verification
            user.email_verified_at = datetime.utcnow()

        db.session.add(user)
        db.session.commit()

        if current_user.is_authenticated and current_user.role == "SuperAdmin":
            flash("User created", "success")
            return redirect(url_for("superadmin.dashboard"))

        code = mfa_service.generate_code()
        ttl = current_app.config.get("OTP_TTL_MIN", 10)
        EmailVerification = current_app.EmailVerification
        ev = EmailVerification(
            user_id=user.id,
            code_hash=mfa_service.hash_code(code),
            expires_at=datetime.utcnow() + timedelta(minutes=ttl),
            last_sent_at=datetime.utcnow(),
            requester_ip=request.remote_addr,
            user_agent=request.headers.get("User-Agent"),
        )
        db.session.add(ev)
        db.session.commit()
        mfa_service.send_signup_email(user, code, ttl, request)
        session["email_verify_id"] = ev.id
        flash("Verification code sent. Check your email.", "info")
        return redirect(url_for("auth.signup_verify"))

    return render_template("auth/signup.html", form=form)


@auth_bp.route("/signup/verify", methods=["GET", "POST"])
def signup_verify():
    """Verify the email code sent during signup."""

    form = EmailCodeForm()
    ev_id = session.get("email_verify_id")
    EmailVerification = current_app.EmailVerification
    ev = EmailVerification.query.get(ev_id) if ev_id else None
    if not ev:
        flash("Start signup first", "error")
        return redirect(url_for("auth.signup"))

    if form.validate_on_submit():
        if datetime.utcnow() > ev.expires_at:
            current_app.db.session.delete(ev)
            current_app.db.session.commit()
            session.pop("email_verify_id", None)
            flash("Code expired. Sign up again.", "error")
            return redirect(url_for("auth.signup"))
        ev.attempts += 1
        if mfa_service.verify_code(form.code.data, ev.code_hash):
            user = ev.user
            user.email_verified_at = datetime.utcnow()
            current_app.db.session.delete(ev)
            current_app.db.session.commit()
            session.pop("email_verify_id", None)
            flash("Email verified. You can log in.", "success")
            return redirect(url_for("auth.login"))
        current_app.db.session.commit()
        flash("Invalid code", "error")
    return render_template("auth/signup_verify.html", form=form)


@auth_bp.route("/logout")
def logout():
    """Log out the current user."""

    if current_user.is_authenticated:
        logout_user()
        flash("Logged out", "success")
    return redirect(url_for("auth.login"))


# Register additional auth routes
from . import forgot_password  # noqa: E402,F401
from . import mfa  # noqa: E402,F401

