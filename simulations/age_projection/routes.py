from __future__ import annotations

"""Routes for the age-based risk projection."""

from flask import jsonify
from flask_login import login_required

from services.auth import role_required

from . import age_projection_bp


@age_projection_bp.get("/api")
@login_required
@role_required(["Doctor", "SuperAdmin"])
def project() -> tuple:
    """Return placeholder projection data.

    The real implementation will calculate risk percentages across a range of
    ages. This stub allows front-end development to proceed independently.
    """

    return jsonify({"ages": [], "risks": []}), 200
