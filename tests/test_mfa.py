import secrets
from werkzeug.security import generate_password_hash
from auth.totp import random_base32, generate_totp


def test_login_with_totp(client, app):
    from app import db, User
    with app.app_context():
        user = User(username="mfauser", email="mfa@example.com", status="approved")
        user.password_hash = generate_password_hash("Passw0rd!")
        user.mfa_enabled = True
        secret = random_base32()
        user.set_mfa_secret(secret)
        code = secrets.token_hex(8)
        from auth.forgot import _hash_code
        user.mfa_recovery_hashes = [_hash_code(code)]
        db.session.add(user)
        db.session.commit()
    resp = client.post(
        "/auth/login",
        data={"identifier": "mfa@example.com", "password": "Passw0rd!"},
    )
    assert resp.status_code == 302 and resp.headers["Location"].endswith("/auth/mfa/verify")
    resp2 = client.post(
        "/auth/mfa/verify",
        data={"code": generate_totp(secret)},
        follow_redirects=True,
    )
    assert b"Predictive insights" in resp2.data


def test_login_with_recovery_code(client, app):
    from app import db, User
    from auth.forgot import _hash_code
    with app.app_context():
        user = User(username="mfauser2", email="mfa2@example.com", status="approved")
        user.password_hash = generate_password_hash("Passw0rd!")
        user.mfa_enabled = True
        secret = random_base32()
        user.set_mfa_secret(secret)
        rec = secrets.token_hex(8)
        user.mfa_recovery_hashes = [_hash_code(rec)]
        db.session.add(user)
        db.session.commit()
    client.post(
        "/auth/login",
        data={"identifier": "mfa2@example.com", "password": "Passw0rd!"},
    )
    resp = client.post(
        "/auth/mfa/verify",
        data={"code": rec},
        follow_redirects=True,
    )
    assert b"Predictive insights" in resp.data
