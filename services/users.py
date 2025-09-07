"""User lookup helpers."""
from __future__ import annotations
from flask import current_app

def get_user_by_email(email: str):
    User = current_app.User
    return User.query.filter_by(email=email).first()
