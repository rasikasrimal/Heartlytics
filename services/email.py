from __future__ import annotations

import smtplib
import ssl
from email.message import EmailMessage
from email.utils import make_msgid
from datetime import datetime
from collections import deque
from typing import Optional

from flask import current_app

_events = deque(maxlen=50)


def _mask(addr: str) -> str:
    try:
        local, domain = addr.split("@")
    except ValueError:
        return addr
    if len(local) <= 2:
        return local[0] + "*" * (len(local) - 1) + "@" + domain
    return f"{local[0]}••••{local[-1]}@{domain}"


def get_events() -> list[dict]:
    """Return recent email events for diagnostics."""
    return list(_events)


class EmailService:
    """Simple SMTP email sender with structured logging."""

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.email_service = self
        self.app = app

    def send_mail(
        self,
        to_address: str,
        subject: str,
        text_body: str,
        html_body: Optional[str] = None,
        *,
        purpose: str = "generic",
    ) -> Optional[str]:
        cfg = self.app.config
        host = cfg.get("SMTP_HOST")
        port = cfg.get("SMTP_PORT", 587)
        username = cfg.get("SMTP_USERNAME")
        password = cfg.get("SMTP_PASSWORD")
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = cfg.get("MAIL_FROM", username)
        msg["To"] = to_address
        if cfg.get("MAIL_REPLY_TO"):
            msg["Reply-To"] = cfg.get("MAIL_REPLY_TO")
        msg["Message-ID"] = make_msgid()
        msg.set_content(text_body)
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        self.app.logger.info(
            "email.send.requested to=%s purpose=%s msgid=%s",
            _mask(to_address),
            purpose,
            msg["Message-ID"],
        )

        try:
            with smtplib.SMTP(host, port, timeout=10) as smtp:
                smtp.starttls(context=ssl.create_default_context())
                self.app.logger.info(
                    "email.send.dispatched host=%s port=%s tls=starttls", host, port
                )
                if username and password:
                    smtp.login(username, password)
                refused = smtp.send_message(msg)
        except smtplib.SMTPAuthenticationError as exc:  # pragma: no cover - network
            self.app.logger.error("email.send.error auth failed")
            _events.append(
                {
                    "ts": datetime.utcnow(),
                    "to": _mask(to_address),
                    "msgid": msg["Message-ID"],
                    "status": "auth",
                }
            )
            return None
        except Exception as exc:  # pragma: no cover - network
            self.app.logger.error("email.send.error network reason=%s", exc)
            _events.append(
                {
                    "ts": datetime.utcnow(),
                    "to": _mask(to_address),
                    "msgid": msg["Message-ID"],
                    "status": "network",
                }
            )
            return None

        accepted = [] if refused else [to_address]
        self.app.logger.info(
            "email.send.response accepted=%s rejected=%s",
            [_mask(a) for a in accepted],
            {k: v[0] for k, v in refused.items()},
        )
        _events.append(
            {
                "ts": datetime.utcnow(),
                "to": _mask(to_address),
                "msgid": msg["Message-ID"],
                "status": "sent" if not refused else "refused",
            }
        )
        return msg["Message-ID"]
