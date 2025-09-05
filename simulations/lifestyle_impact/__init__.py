from __future__ import annotations

"""Lifestyle Impact simulation module."""

from flask import Blueprint

lifestyle_impact_bp = Blueprint("lifestyle_impact", __name__, url_prefix="/lifestyle-impact")

from . import routes  # noqa: E402,F401
