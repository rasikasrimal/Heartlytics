from __future__ import annotations

"""User blueprint for basic prediction access."""

from flask import Blueprint

user_bp = Blueprint("user", __name__, template_folder="templates", url_prefix="/user")

from . import routes  # noqa: E402,F401
