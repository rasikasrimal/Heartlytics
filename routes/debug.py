from __future__ import annotations

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from auth.decorators import require_roles
from services.email import get_events


debug_bp = Blueprint("debug", __name__, url_prefix="/debug")


@debug_bp.get("/theme")
@login_required
def theme_page():
    """Simple page used as a smoke test for client-side theming."""
    return render_template("debug/theme.html")


@debug_bp.route("/mail", methods=["GET", "POST"])
@login_required
@require_roles("SuperAdmin")
def mail_debug():
    """Send a test email and show recent events."""
    if request.method == "POST":
        addr = request.form.get("address", "")
        if addr:
            try:
                current_app.email_service.send_mail(
                    addr,
                    "Your verification code",
                    "This is a test email from Heartlytics.",
                    "<p>This is a test email from Heartlytics.</p>",
                    purpose="debug",
                )
                flash("Test email sent", "success")
            except Exception:
                flash("Failed to send email", "error")
        return redirect(url_for("debug.mail_debug"))
    events = get_events()
    return render_template("debug/mail.html", events=events)
