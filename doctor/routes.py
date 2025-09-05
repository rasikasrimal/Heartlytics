from __future__ import annotations

"""Routes for doctor-specific functionality."""

from flask import render_template
from flask_login import current_user, login_required

from services.auth import role_required

from . import doctor_bp


@doctor_bp.route("/")
@login_required
@role_required(["Doctor"])
def dashboard():
    """Display patients entered by the logged-in doctor."""
    from app import Patient  # local import to avoid circular

    patients = (
        Patient.query.filter_by(entered_by_user_id=current_user.id)
        .order_by(Patient.created_at.desc())
        .all()
    )
    return render_template("doctor/dashboard.html", patients=patients)
