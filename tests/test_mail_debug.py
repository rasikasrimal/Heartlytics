import smtplib


def test_mail_debug_events(superadmin_client, monkeypatch):
    app = superadmin_client.application
    app.config.update(
        {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": 587,
            "SMTP_USERNAME": "user@example.com",
            "SMTP_PASSWORD": "pass",
            "MAIL_FROM": "user@example.com",
        }
    )

    class DummySMTP:
        def __init__(self, host, port, timeout=10):
            self.host = host
            self.port = port

        def starttls(self, context=None):
            pass

        def login(self, user, password):
            pass

        def send_message(self, msg):
            self.msg = msg
            return {}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

    monkeypatch.setattr("services.email.smtplib.SMTP", DummySMTP)

    resp = superadmin_client.post(
        "/debug/mail",
        data={"address": "dest@example.com"},
        follow_redirects=True,
    )
    assert b"Test email sent" in resp.data
    assert b"dest@example.com" not in resp.data  # address masked
