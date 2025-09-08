from __future__ import annotations

from flask import g, request

def init_theme(app):
    """Register hooks to expose the user's theme preference.

    The theme is stored client-side via a cookie named ``theme``.  This
    helper reads the cookie on each request and injects a ``theme`` template
    variable so server-side rendering matches the user's preference and avoids
    a flash of incorrect theme during page load.
    """

    @app.before_request
    def _load_theme_from_cookie():
        raw = request.headers.get("Cookie", "")
        theme = "light"
        for part in raw.split(";"):
            part = part.strip()
            if part.startswith("theme="):
                theme = part.split("=", 1)[1]
                break
        g.theme = theme

    @app.context_processor
    def _inject_theme():
        return {"theme": getattr(g, "theme", "light")}
