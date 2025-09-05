"""Super Admin interface for managing all users."""

from __future__ import annotations

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required
from sqlalchemy import func, or_
from datetime import datetime, timedelta
import secrets

from services.auth import role_required
from services.security import csrf_protect

superadmin_bp = Blueprint("superadmin", __name__, url_prefix="/superadmin")


@superadmin_bp.route("/")
@login_required
@role_required(["SuperAdmin", "Admin"])
def dashboard():
    """Display user management dashboard with search/sort/pagination."""
    db = current_app.db
    User = current_app.User

    q = request.args.get("q", "").strip()
    sort = request.args.get("sort", "date")
    order = request.args.get("order", "desc")
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 10))
    query_args = request.args.to_dict()
    query_args.pop("page", None)

    query = User.query.filter(User.role != "SuperAdmin")
    if current_user.role == "Admin":
        query = query.filter(User.role == "Doctor")
    if q:
        like = f"%{q}%"
        query = query.filter(or_(User.username.ilike(like), User.email.ilike(like)))

    sort_map = {
        "role": User.role,
        "status": User.status,
        "date": User.created_at,
    }
    sort_col = sort_map.get(sort, User.created_at)
    sort_col = sort_col.asc() if order == "asc" else sort_col.desc()
    query = query.order_by(sort_col)

    pagination = query.paginate(page=page, per_page=per_page)
    users = pagination.items

    if current_user.role == "Admin":
        stats = {
            "total_users": User.query.filter(User.role == "Doctor").count(),
            "active_doctors": User.query.filter_by(role="Doctor", status="approved").count(),
            "pending": User.query.filter_by(role="Doctor", status="pending").count(),
            "suspended": User.query.filter_by(role="Doctor", status="suspended").count(),
        }
    else:
        stats = {
            "total_users": User.query.filter(User.role != "SuperAdmin").count(),
            "active_doctors": User.query.filter_by(role="Doctor", status="approved").count(),
            "pending": User.query.filter_by(status="pending").count(),
            "suspended": User.query.filter_by(status="suspended").count(),
        }

    trend_query = db.session.query(func.strftime("%Y-%W", User.created_at), func.count())
    if current_user.role == "Admin":
        trend_query = trend_query.filter(User.role == "Doctor")
    trend_rows = (
        trend_query
        .group_by(func.strftime("%Y-%W", User.created_at))
        .order_by(func.strftime("%Y-%W", User.created_at))
        .all()
    )
    trend_labels = [r[0] for r in trend_rows]
    trend_values = [r[1] for r in trend_rows]

    return render_template(
        "superadmin/dashboard.html",
        users=users,
        pagination=pagination,
        stats=stats,
        trend_labels=trend_labels,
        trend_values=trend_values,
        query_args=query_args,
    )


@superadmin_bp.post("/users/<int:user_id>/approve")
@login_required
@role_required(["SuperAdmin", "Admin"])
@csrf_protect
def approve_user(user_id: int):
    db = current_app.db
    User = current_app.User
    AuditLog = current_app.AuditLog
    user = User.query.get_or_404(user_id)
    if current_user.role == "Admin" and user.role != "Doctor":
        flash("Admins can only approve doctors", "error")
        return redirect(url_for("superadmin.dashboard"))
    old = user.status
    user.status = "approved"
    db.session.add(
        AuditLog(
            acting_user_id=current_user.id,
            target_user_id=user.id,
            action="approve",
            old_value=old,
            new_value="approved",
        )
    )
    db.session.commit()
    flash("User approved", "success")
    return redirect(url_for("superadmin.dashboard"))


@superadmin_bp.post("/users/<int:user_id>/reject")
@login_required
@role_required(["SuperAdmin", "Admin"])
@csrf_protect
def reject_user(user_id: int):
    db = current_app.db
    User = current_app.User
    AuditLog = current_app.AuditLog
    user = User.query.get_or_404(user_id)
    if current_user.role == "Admin" and user.role != "Doctor":
        flash("Admins can only reject doctors", "error")
        return redirect(url_for("superadmin.dashboard"))
    old = user.status
    user.status = "rejected"
    db.session.add(
        AuditLog(
            acting_user_id=current_user.id,
            target_user_id=user.id,
            action="reject",
            old_value=old,
            new_value="rejected",
        )
    )
    db.session.commit()
    flash("User rejected", "success")
    return redirect(url_for("superadmin.dashboard"))


@superadmin_bp.post("/users/<int:user_id>/promote")
@login_required
@role_required(["SuperAdmin"])
@csrf_protect
def promote_user(user_id: int):
    db = current_app.db
    User = current_app.User
    AuditLog = current_app.AuditLog
    user = User.query.get_or_404(user_id)
    if user.role == "Doctor":
        old_role = user.role
        user.role = "Admin"
        user.status = "approved"
        db.session.add(
            AuditLog(
                acting_user_id=current_user.id,
                target_user_id=user.id,
                action="promote",
                old_value=old_role,
                new_value="Admin",
            )
        )
        db.session.commit()
        flash("User promoted to Admin", "success")
    return redirect(url_for("superadmin.dashboard"))


@superadmin_bp.post("/users/<int:user_id>/role")
@login_required
@role_required(["SuperAdmin", "Admin"])
@csrf_protect
def update_role(user_id: int):
    """Update a user's role among User, Doctor or Admin."""
    db = current_app.db
    User = current_app.User
    AuditLog = current_app.AuditLog
    user = User.query.get_or_404(user_id)
    if user.role == "SuperAdmin":
        flash("Cannot modify SuperAdmin role", "danger")
        return redirect(url_for("superadmin.dashboard"))
    new_role = request.form.get("role")
    allowed_roles = {"User", "Doctor", "Admin"}
    if current_user.role == "Admin":
        allowed_roles = {"User", "Doctor"}
        if user.role not in {"Doctor", "User"}:
            flash("Admins can only modify doctor or user roles", "error")
            return redirect(url_for("superadmin.dashboard"))
    if new_role not in allowed_roles:
        return redirect(url_for("superadmin.dashboard"))
    old = user.role
    if old != new_role:
        user.role = new_role
        db.session.add(
            AuditLog(
                acting_user_id=current_user.id,
                target_user_id=user.id,
                action="change_role",
                old_value=old,
                new_value=new_role,
            )
        )
        db.session.commit()
        flash("Role updated", "success")
    return redirect(url_for("superadmin.dashboard"))


@superadmin_bp.post("/users/<int:user_id>/status")
@login_required
@role_required(["SuperAdmin", "Admin"])
@csrf_protect
def toggle_status(user_id: int):
    """Suspend or unsuspend an approved user."""
    db = current_app.db
    User = current_app.User
    AuditLog = current_app.AuditLog
    user = User.query.get_or_404(user_id)
    if user.role == "SuperAdmin" or user.id == current_user.id:
        flash("Cannot modify SuperAdmin status", "danger")
        return redirect(url_for("superadmin.dashboard"))
    if current_user.role == "Admin" and user.role != "Doctor":
        flash("Admins can only update doctor status", "error")
        return redirect(url_for("superadmin.dashboard"))
    if user.status not in {"approved", "suspended"}:
        return redirect(url_for("superadmin.dashboard"))
    old = user.status
    user.status = "suspended" if user.status == "approved" else "approved"
    db.session.add(
        AuditLog(
            acting_user_id=current_user.id,
            target_user_id=user.id,
            action="toggle_status",
            old_value=old,
            new_value=user.status,
        )
    )
    db.session.commit()
    flash("Status updated", "success")
    return redirect(url_for("superadmin.dashboard"))


@superadmin_bp.post("/users/<int:user_id>/reset_password")
@login_required
@role_required(["SuperAdmin", "Admin"])
@csrf_protect
def reset_password(user_id: int):
    """Set a temporary password for a user."""
    db = current_app.db
    User = current_app.User
    AuditLog = current_app.AuditLog
    user = User.query.get_or_404(user_id)
    if current_user.role == "Admin" and user.role != "Doctor":
        flash("Admins can only reset doctor passwords", "error")
        return redirect(url_for("superadmin.dashboard"))
    temp_pw = secrets.token_urlsafe(8)
    user.set_password(temp_pw)
    db.session.add(
        AuditLog(
            acting_user_id=current_user.id,
            target_user_id=user.id,
            action="reset_password",
            new_value="temporary",
        )
    )
    db.session.commit()
    flash(f"Temporary password: {temp_pw}", "info")
    return redirect(url_for("superadmin.dashboard"))


@superadmin_bp.route("/audit")
@login_required
@role_required(["SuperAdmin", "Admin"])
def audit_logs():
    """Display audit trail of administrative actions with filtering."""
    AuditLog = current_app.AuditLog
    User = current_app.User

    username = request.args.get("username", "").strip()
    role = request.args.get("role", "").strip()
    action_type = request.args.get("action", "").strip()
    start = request.args.get("start", "").strip()
    end = request.args.get("end", "").strip()
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))
    query_args = request.args.to_dict()
    query_args.pop("page", None)

    query = AuditLog.query.join(User, AuditLog.target_user)
    if username:
        query = query.filter(User.username.ilike(f"%{username}%"))
    if role:
        query = query.filter(User.role == role)
    if action_type:
        query = query.filter(AuditLog.action == action_type)
    if start:
        try:
            start_dt = datetime.strptime(start, "%Y-%m-%d")
            query = query.filter(AuditLog.timestamp >= start_dt)
        except ValueError:
            pass
    if end:
        try:
            end_dt = datetime.strptime(end, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(AuditLog.timestamp < end_dt)
        except ValueError:
            pass

    query = query.order_by(AuditLog.timestamp.desc())
    pagination = query.paginate(page=page, per_page=per_page)
    logs = pagination.items

    return render_template(
        "superadmin/audit.html", logs=logs, pagination=pagination, query_args=query_args
    )
