from __future__ import annotations

"""Routes for doctor-specific functionality."""

from flask import render_template, current_app
from flask_login import current_user, login_required

from auth.decorators import require_roles

from . import doctor_bp


@doctor_bp.route("/")
@login_required
@require_roles("Doctor")
def dashboard():
    """Display patients entered by the logged-in doctor."""
    db = current_app.extensions["sqlalchemy"]
    Patient = db.Model.registry._class_registry.get("Patient")

    patients = (
        Patient.query.filter_by(entered_by_user_id=current_user.id)
        .order_by(Patient.created_at.desc())
        .all()
    )
    return render_template("doctor/dashboard.html", patients=patients)
