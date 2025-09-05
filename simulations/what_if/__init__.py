from __future__ import annotations

"""What-If simulation module."""

from flask import Blueprint

what_if_bp = Blueprint("what_if", __name__, url_prefix="/what-if")

from . import routes  # noqa: E402,F401
