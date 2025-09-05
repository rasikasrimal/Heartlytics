from __future__ import annotations

"""Routes for regular users who can make predictions."""

from flask import render_template
from flask_login import login_required

from services.auth import role_required

from . import user_bp


@user_bp.route("/")
@login_required
@role_required(["User"])
def dashboard():
    """Simple dashboard with link to prediction page."""
    return render_template("user/dashboard.html")
