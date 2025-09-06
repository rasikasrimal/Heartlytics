from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import login_required


debug_bp = Blueprint("debug", __name__, url_prefix="/debug")


@debug_bp.get("/theme")
@login_required
def theme_page():
    """Simple page used as a smoke test for client-side theming."""
    return render_template("debug/theme.html")
