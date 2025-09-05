from __future__ import annotations

"""Routes for lifestyle change simulations."""

from flask import jsonify
from flask_login import login_required

from services.auth import role_required

from . import lifestyle_impact_bp


@lifestyle_impact_bp.get("/api")
@login_required
@role_required(["Doctor", "SuperAdmin"])
def simulate() -> tuple:
    """Return placeholder before/after comparison.

    In future iterations this will recompute risk based on predefined lifestyle
    modifications. The stub keeps the API stable for front-end work.
    """

    return jsonify({"before": 0, "after": 0}), 200
