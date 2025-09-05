from __future__ import annotations

"""Doctor blueprint for managing their own patients and predictions."""

from flask import Blueprint

# Template files are stored within this package's ``templates`` directory.
doctor_bp = Blueprint("doctor", __name__, template_folder="templates", url_prefix="/doctor")

from . import routes  # noqa: E402,F401
