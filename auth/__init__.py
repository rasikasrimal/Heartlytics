"""Authentication blueprint handling user login, sign-up and logout."""

from __future__ import annotations

from datetime import datetime, timedelta

from flask import Blueprint, current_app, flash, redirect, render_template, session, url_for, request, jsonify
from flask_login import login_user, logout_user, current_user
from sqlalchemy import or_

from services.mfa import generate_code, hash_code, send_reset_email

from .forms import LoginForm, SignupForm


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


@auth_bp.get("/check-username")
def check_username():
    """Return availability of a username."""
    User = current_app.User
    username = request.args.get("username", "").strip()
    exists = User.query.filter_by(username=username).first() is not None
    return jsonify({"available": not exists})


@auth_bp.get("/check-email")
def check_email():
    """Return availability of an email."""
    User = current_app.User
    email = request.args.get("email", "").strip()
    exists = User.query.filter_by(email=email).first() is not None
    return jsonify({"available": not exists})


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

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            if User.query.filter_by(username=form.username.data).first():
                return jsonify({"error": "username"}), 400
            if User.query.filter_by(email=form.email.data).first():
                return jsonify({"error": "email"}), 400

            if form.nickname.data and User.query.filter_by(nickname=form.nickname.data).first():
                return jsonify({"error": "nickname"}), 400

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

            db.session.add(user)
            db.session.commit()

            code = generate_code()
            session["signup_otp"] = hash_code(code)
            session["signup_user"] = user.id
            send_reset_email(user, code, current_app.config.get("OTP_TTL", 10), request)
            return jsonify({"success": True})

        # Prevent duplicate usernames/emails.
        if User.query.filter_by(username=form.username.data).first():
            flash("Username taken", "error")
            return render_template("auth/signup.html", form=form)
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered, sign in?", "error")
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

        db.session.add(user)
        db.session.commit()

        if current_user.is_authenticated and current_user.role == "SuperAdmin":
            flash("User created", "success")
            return redirect(url_for("superadmin.dashboard"))

        if status == "approved":
            flash("Account created. You can log in.", "success")
        else:
            flash("Signup request submitted. Await approval", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/signup.html", form=form)


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

