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

from auth.decorators import require_roles
from services.security import csrf_protect
from services.crypto import envelope, get_keyring

superadmin_bp = Blueprint("superadmin", __name__, url_prefix="/superadmin")


@superadmin_bp.route("/")
@login_required
@require_roles("SuperAdmin", "Admin")
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
@require_roles("SuperAdmin", "Admin")
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
@require_roles("SuperAdmin", "Admin")
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
@require_roles("SuperAdmin")
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
@require_roles("SuperAdmin", "Admin")
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
@require_roles("SuperAdmin", "Admin")
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
@require_roles("SuperAdmin", "Admin")
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
@require_roles("SuperAdmin", "Admin")
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


# ---------------------------
# Encryption demo (SuperAdmin only)
# ---------------------------

def _patient_blob_b64(p):
    import base64
    if not p or not p.patient_data_ct:
        return None
    return {
        "ciphertext": base64.b64encode(p.patient_data_ct).decode(),
        "nonce": base64.b64encode(p.patient_data_nonce or b"").decode(),
        "tag": base64.b64encode(p.patient_data_tag or b"").decode(),
        "wrapped_dk": base64.b64encode(p.patient_data_wrapped_dk or b"").decode(),
        "kid": p.patient_data_kid,
        "kver": p.patient_data_kver,
    }


@superadmin_bp.route("/encryption")
@login_required
@require_roles("SuperAdmin")
def encryption_index():
    """Landing page to search/select patient records for encryption demo."""
    Patient = current_app.Patient
    Prediction = current_app.Prediction
    q = (request.args.get("id") or "").strip()
    patient = None
    if q.isdigit():
        pid = int(q)
        patient = Patient.query.get(pid)
        if patient is not None:
            return redirect(url_for("superadmin.encryption_view", pid=patient.id))
        # try prediction id fallback (IDs from dashboard typically refer to predictions)
        pred = Prediction.query.get(pid)
        if pred is not None:
            return redirect(url_for("superadmin.encryption_view_pred", pred_id=pred.id))
        flash("Record not found (patient or prediction)", "warning")
    recent = Patient.query.order_by(Patient.created_at.desc()).limit(10).all()
    return render_template(
        "superadmin/encryption.html",
        patient=patient,
        blob=_patient_blob_b64(patient) if patient else None,
        recent=recent,
        decrypted=None,
        error=None,
        can_decrypt=bool(current_app.config.get("DEV_KMS_MASTER_KEY")),
    )


@superadmin_bp.route("/encryption/<int:pid>")
@login_required
@require_roles("SuperAdmin")
def encryption_view(pid: int):
    """Show envelope components for a patient record and log the view."""
    Patient = current_app.Patient
    AuditLog = current_app.AuditLog
    db = current_app.db
    p = Patient.query.get_or_404(pid)
    db.session.add(
        AuditLog(
            acting_user_id=current_user.id,
            target_user_id=p.entered_by_user_id,
            action="encryption_view",
            new_value=f"patient_id={p.id}",
        )
    )
    db.session.commit()
    return render_template(
        "superadmin/encryption.html",
        patient=p,
        blob=_patient_blob_b64(p),
        recent=[],
        decrypted=None,
        error=None,
        subject="patient",
        decrypt_action=url_for("superadmin.encryption_decrypt", pid=p.id),
        decrypted_header="Decrypted JSON",
        can_decrypt=bool(current_app.config.get("DEV_KMS_MASTER_KEY")),
    )


@superadmin_bp.post("/encryption/<int:pid>/decrypt")
@login_required
@require_roles("SuperAdmin")
@csrf_protect
def encryption_decrypt(pid: int):
    """Attempt local decryption using server-side key; never expose keys."""
    Patient = current_app.Patient
    AuditLog = current_app.AuditLog
    db = current_app.db
    p = Patient.query.get_or_404(pid)
    decrypted = None
    error = None
    if not current_app.config.get("DEV_KMS_MASTER_KEY"):
        error = "Master key not available on server"
    else:
        try:
            blob = {
                "ciphertext": p.patient_data_ct,
                "nonce": p.patient_data_nonce,
                "tag": p.patient_data_tag,
                "wrapped_dk": p.patient_data_wrapped_dk,
                "kid": p.patient_data_kid,
                "kver": p.patient_data_kver,
            }
            ctx = f"{p.__tablename__}:patient_data|{p.patient_data_kid}|{p.patient_data_kver}"
            pt = envelope.decrypt_field(blob, ctx)
            import json as _json
            decrypted = _json.dumps(_json.loads(pt.decode("utf-8")), indent=2)
        except Exception as exc:
            error = f"Decrypt failed: {type(exc).__name__}"
    db.session.add(
        AuditLog(
            acting_user_id=current_user.id,
            target_user_id=p.entered_by_user_id,
            action="encryption_decrypt",
            new_value=f"patient_id={p.id} ok={error is None}",
        )
    )
    db.session.commit()
    return render_template(
        "superadmin/encryption.html",
        patient=p,
        blob=_patient_blob_b64(p),
        recent=[],
        decrypted=decrypted,
        error=error,
        subject="patient",
        decrypt_action=url_for("superadmin.encryption_decrypt", pid=p.id),
        decrypted_header="Decrypted JSON",
        can_decrypt=bool(current_app.config.get("DEV_KMS_MASTER_KEY")),
    )


def _prediction_blob_b64(pred):
    import base64
    if not pred or not pred.patient_name_ct:
        return None
    return {
        "ciphertext": base64.b64encode(pred.patient_name_ct).decode(),
        "nonce": base64.b64encode(pred.patient_name_nonce or b"").decode(),
        "tag": base64.b64encode(pred.patient_name_tag or b"").decode(),
        "wrapped_dk": base64.b64encode(pred.patient_name_wrapped_dk or b"").decode(),
        "kid": pred.patient_name_kid,
        "kver": pred.patient_name_kver,
    }


@superadmin_bp.route("/encryption/pred/<int:pred_id>")
@login_required
@require_roles("SuperAdmin")
def encryption_view_pred(pred_id: int):
    """Show envelope components for encrypted patient_name on a Prediction."""
    Prediction = current_app.Prediction
    AuditLog = current_app.AuditLog
    db = current_app.db
    pr = Prediction.query.get_or_404(pred_id)
    db.session.add(
        AuditLog(
            acting_user_id=current_user.id,
            target_user_id=current_user.id,
            action="encryption_view_pred",
            new_value=f"prediction_id={pr.id}",
        )
    )
    db.session.commit()
    return render_template(
        "superadmin/encryption.html",
        prediction=pr,
        blob=_prediction_blob_b64(pr),
        recent=[],
        decrypted=None,
        error=None,
        subject="prediction",
        decrypt_action=url_for("superadmin.encryption_decrypt_pred", pred_id=pr.id),
        decrypted_header="Decrypted Patient Name",
        can_decrypt=bool(current_app.config.get("DEV_KMS_MASTER_KEY")),
    )


@superadmin_bp.post("/encryption/pred/<int:pred_id>/decrypt")
@login_required
@require_roles("SuperAdmin")
@csrf_protect
def encryption_decrypt_pred(pred_id: int):
    """Attempt local decryption of prediction.patient_name envelope."""
    Prediction = current_app.Prediction
    AuditLog = current_app.AuditLog
    db = current_app.db
    pr = Prediction.query.get_or_404(pred_id)
    decrypted = None
    error = None
    if not current_app.config.get("DEV_KMS_MASTER_KEY"):
        error = "Master key not available on server"
    else:
        try:
            blob = {
                "ciphertext": pr.patient_name_ct,
                "nonce": pr.patient_name_nonce,
                "tag": pr.patient_name_tag,
                "wrapped_dk": pr.patient_name_wrapped_dk,
                "kid": pr.patient_name_kid,
                "kver": pr.patient_name_kver,
            }
            ctx = f"{pr.__tablename__}:patient_name|{pr.patient_name_kid}|{pr.patient_name_kver}"
            pt = envelope.decrypt_field(blob, ctx)
            decrypted = pt.decode("utf-8", errors="replace")
        except Exception as exc:
            error = f"Decrypt failed: {type(exc).__name__}"
    db.session.add(
        AuditLog(
            acting_user_id=current_user.id,
            target_user_id=current_user.id,
            action="encryption_decrypt_pred",
            new_value=f"prediction_id={pr.id} ok={error is None}",
        )
    )
    db.session.commit()
    return render_template(
        "superadmin/encryption.html",
        prediction=pr,
        blob=_prediction_blob_b64(pr),
        recent=[],
        decrypted=decrypted,
        error=error,
        subject="prediction",
        decrypt_action=url_for("superadmin.encryption_decrypt_pred", pred_id=pr.id),
        decrypted_header="Decrypted Patient Name",
        can_decrypt=bool(current_app.config.get("DEV_KMS_MASTER_KEY")),
    )


@superadmin_bp.post("/encryption/pred/<int:pred_id>/set_name")
@login_required
@require_roles("SuperAdmin")
@csrf_protect
def encryption_set_name_pred(pred_id: int):
    """Set or update patient_name on a Prediction (encrypted if enabled)."""
    Prediction = current_app.Prediction
    AuditLog = current_app.AuditLog
    db = current_app.db
    pr = Prediction.query.get_or_404(pred_id)
    name = (request.form.get("patient_name") or "").strip()
    if not name:
        flash("Name cannot be empty", "warning")
        return redirect(url_for("superadmin.encryption_view_pred", pred_id=pred_id))
    try:
        pr.patient_name = name  # uses encrypted setter if enabled
        db.session.add(
            AuditLog(
                acting_user_id=current_user.id,
                target_user_id=current_user.id,
                action="encryption_set_name_pred",
                new_value=f"prediction_id={pr.id}",
            )
        )
        db.session.commit()
        flash("Patient name set for this prediction", "success")
    except Exception as exc:
        db.session.rollback()
        flash(f"Failed to set name: {type(exc).__name__}", "error")
    return redirect(url_for("superadmin.encryption_view_pred", pred_id=pred_id))
