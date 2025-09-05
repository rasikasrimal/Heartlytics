from __future__ import annotations

import secrets
from functools import wraps
from flask import request, session, abort, jsonify


def csrf_protect(fn):
    """Simple form-based CSRF protection decorator."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return fn(*args, **kwargs)
        token_form = request.form.get("_csrf_token")
        token_sess = session.get("_csrf_token")
        if token_form and token_sess and token_form == token_sess:
            return fn(*args, **kwargs)
        abort(400, "Invalid CSRF token")
    return wrapper


def get_csrf_token():
    """Return a session CSRF token, creating one if necessary."""
    token = session.get('_csrf_token')
    if not token:
        token = secrets.token_urlsafe(32)
        session['_csrf_token'] = token
    return token


def get_csrf_from_header():
    """Retrieve CSRF token from common header names."""
    return request.headers.get("X-CSRF-Token") or request.headers.get("X-CSRFToken")


def csrf_protect_api(fn):
    """API CSRF protection decorator using headers."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token_req = get_csrf_from_header()
        token_sess = session.get("_csrf_token")
        if token_req and token_sess and token_req == token_sess:
            return fn(*args, **kwargs)
        return jsonify({"ok": False, "error": "Invalid CSRF token"}), 400
    return wrapper
