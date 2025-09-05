from __future__ import annotations

"""Blueprint registration for the simulations module."""

from flask import Blueprint, render_template
from flask_login import login_required

from services.auth import role_required

# Main blueprint exposing the /simulations namespace
simulations_bp = Blueprint(
    "simulations", __name__, url_prefix="/simulations", template_folder="templates"
)

@simulations_bp.route("/")
@login_required
@role_required(["Doctor", "SuperAdmin"])
def dashboard():
    """Render the simulations dashboard.

    The page itself only bootstraps the front-end modules. Each simulation
    feature lives in its own sub-blueprint so teams can develop them in
    parallel without touching this file.
    """

    return render_template("dashboard.html")


def register_simulations(app) -> None:
    """Register simulation submodules based on feature flags."""

    if app.config.get("ENABLE_WHAT_IF", True):
        from .what_if import what_if_bp

        simulations_bp.register_blueprint(what_if_bp)
    if app.config.get("ENABLE_AGE_PROJECTION", True):
        from .age_projection import age_projection_bp

        simulations_bp.register_blueprint(age_projection_bp)
    if app.config.get("ENABLE_LIFESTYLE_IMPACT", True):
        from .lifestyle_impact import lifestyle_impact_bp

        simulations_bp.register_blueprint(lifestyle_impact_bp)
