"""Helpers for one-time verification codes (MFA and password resets)."""
from __future__ import annotations

import hashlib
import hmac
import secrets
from datetime import datetime
from flask import current_app


def generate_code(length: int | None = None) -> str:
    """Return a numeric code of ``length`` digits."""
    length = length or current_app.config.get("OTP_LENGTH", 6)
    return "".join(secrets.choice("0123456789") for _ in range(length))


def hash_code(code: str) -> str:
    """Hash ``code`` with pepper using SHA-256."""
    pepper = current_app.config.get("OTP_PEPPER", "")
    return hashlib.sha256((pepper + code).encode()).hexdigest()


def verify_code(code: str, hashed: str) -> bool:
    """Constant-time comparison of ``code`` against ``hashed``."""
    return hmac.compare_digest(hash_code(code), hashed)


def send_reset_email(user, code: str, ttl: int, request) -> None:
    """Send the password reset ``code`` to ``user`` via email.

    Any delivery failures are logged; the exception is swallowed so the flow
    remains enumeration-safe.
    """
    text = (
        f"Your verification code is {code}.\n"
        f"It expires in {ttl} minutes.\n"
        f"Request time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
        f"IP: {request.remote_addr}\n"
        "If this wasn't you, ignore this message."
    )
    html = text.replace("\n", "<br>")
    try:
        current_app.email_service.send_mail(
            user.email, "Your verification code", text, html, purpose="otp"
        )
    except Exception as exc:  # pragma: no cover - network errors
        current_app.logger.error("otp.email.failed user=%s", user.email, exc_info=exc)

