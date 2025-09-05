from __future__ import annotations

"""Age Projection simulation module."""

from flask import Blueprint

age_projection_bp = Blueprint("age_projection", __name__, url_prefix="/age-projection")

from . import routes  # noqa: E402,F401
