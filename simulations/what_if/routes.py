from __future__ import annotations

"""Routes for the What-If simulation."""

from flask import jsonify
from flask_login import login_required

from services.auth import role_required

from . import what_if_bp


@what_if_bp.get("/api")
@login_required
@role_required(["Doctor", "SuperAdmin"])
def simulate() -> tuple:
    """Return placeholder risk data for a single-variable tweak.

    The actual implementation will compute a new risk percentage based on the
    provided variable adjustments. Returning an empty structure keeps the
    endpoint stable during parallel development.
    """

    return jsonify({"points": []}), 200
