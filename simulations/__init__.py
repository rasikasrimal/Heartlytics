from __future__ import annotations

"""Blueprint for simulation pages and modules."""

from flask import Blueprint

simulations_bp = Blueprint("simulations", __name__, template_folder="templates", url_prefix="/simulations")

from . import routes  # noqa: E402,F401
