import secrets
from werkzeug.security import generate_password_hash
from auth.totp import random_base32, generate_totp


def test_login_with_totp(client, app):
    from app import db, User
    with app.app_context():
        User.query.filter_by(email="mfa@example.com").delete()
        db.session.commit()
        user = User(username="mfauser", email="mfa@example.com", status="approved")
        user.password_hash = generate_password_hash("Passw0rd!")
        user.mfa_enabled = True
        secret = random_base32()
        user.set_mfa_secret(secret)
        code = secrets.token_hex(8)
        from services.mfa import hash_code
        user.mfa_recovery_hashes = [hash_code(code)]
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
    assert b"Predict" in resp2.data


def test_login_with_totp_spaces(client, app):
    from app import db, User
    with app.app_context():
        User.query.filter_by(email="mfa3@example.com").delete()
        db.session.commit()
        user = User(username="mfauser3", email="mfa3@example.com", status="approved")
        user.password_hash = generate_password_hash("Passw0rd!")
        user.mfa_enabled = True
        secret = random_base32()
        user.set_mfa_secret(secret)
        db.session.add(user)
        db.session.commit()
    client.post(
        "/auth/login",
        data={"identifier": "mfa3@example.com", "password": "Passw0rd!"},
    )
    code = generate_totp(secret)
    spaced = code[:3] + " " + code[3:]
    resp = client.post(
        "/auth/mfa/verify",
        data={"code": spaced},
        follow_redirects=True,
    )
    assert b"Predict" in resp.data


def test_login_with_totp_hyphen(client, app):
    from app import db, User
    with app.app_context():
        User.query.filter_by(email="mfa4@example.com").delete()
        db.session.commit()
        user = User(username="mfauser4", email="mfa4@example.com", status="approved")
        user.password_hash = generate_password_hash("Passw0rd!")
        user.mfa_enabled = True
        secret = random_base32()
        user.set_mfa_secret(secret)
        db.session.add(user)
        db.session.commit()
    client.post(
        "/auth/login",
        data={"identifier": "mfa4@example.com", "password": "Passw0rd!"},
    )
    code = generate_totp(secret)
    dashed = code[:3] + "-" + code[3:]
    resp = client.post(
        "/auth/mfa/verify",
        data={"code": dashed},
        follow_redirects=True,
    )
    assert b"Predict" in resp.data


def test_login_with_recovery_code(client, app):
    from app import db, User
    from services.mfa import hash_code
    with app.app_context():
        User.query.filter_by(email="mfa2@example.com").delete()
        db.session.commit()
        user = User(username="mfauser2", email="mfa2@example.com", status="approved")
        user.password_hash = generate_password_hash("Passw0rd!")
        user.mfa_enabled = True
        secret = random_base32()
        user.set_mfa_secret(secret)
        rec = secrets.token_hex(8)
        user.mfa_recovery_hashes = [hash_code(rec)]
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
    assert b"Predict" in resp.data


def test_disable_mfa_with_hyphen(client, app):
    from app import db, User
    with app.app_context():
        User.query.filter_by(email="mfa5@example.com").delete()
        db.session.commit()
        user = User(username="mfauser5", email="mfa5@example.com", status="approved")
        user.password_hash = generate_password_hash("Passw0rd!")
        user.mfa_enabled = True
        secret = random_base32()
        user.set_mfa_secret(secret)
        db.session.add(user)
        db.session.commit()
    client.post(
        "/auth/login",
        data={"identifier": "mfa5@example.com", "password": "Passw0rd!"},
    )
    client.post(
        "/auth/mfa/verify",
        data={"code": generate_totp(secret)},
        follow_redirects=True,
    )
    code = generate_totp(secret)
    dashed = code[:3] + "-" + code[3:]
    resp = client.post(
        "/auth/mfa/disable",
        data={"password": "Passw0rd!", "code": dashed},
        follow_redirects=True,
    )
    assert b"Two-step verification disabled" in resp.data


def test_settings_shows_mfa_option(auth_client):
    resp = auth_client.get("/settings/")
    assert b"Two-Step Verification" in resp.data
    assert b"/auth/mfa/setup" in resp.data


def test_login_with_email_code(monkeypatch, client, app):
    from app import db, User
    from auth.totp import random_base32
    with app.app_context():
        User.query.filter_by(email="mfaemail@example.com").delete()
        db.session.commit()
        user = User(username="mfaemail", email="mfaemail@example.com", status="approved")
        user.password_hash = generate_password_hash("Passw0rd!")
        user.mfa_enabled = True
        secret = random_base32()
        user.set_mfa_secret(secret)
        db.session.add(user)
        db.session.commit()
    monkeypatch.setattr("auth.mfa.secrets.choice", lambda seq: seq[0])
    monkeypatch.setattr("services.email.EmailService.send_mail", lambda self, *args, **kwargs: None)
    client.post(
        "/auth/login",
        data={"identifier": "mfaemail@example.com", "password": "Passw0rd!"},
    )
    client.get("/auth/mfa/email")
    resp = client.post(
        "/auth/mfa/email",
        data={"code": "000000"},
        follow_redirects=True,
    )
    assert b"Predict" in resp.data


def test_mfa_verify_masks_email(client, app):
    from app import db, User
    from utils.mask import mask_email
    email = "mask@example.com"
    with app.app_context():
        user = User(username="mask_user", email=email, status="approved")
        user.set_password("Passw0rd!")
        db.session.add(user)
        db.session.commit()
        uid = user.id
    with client.session_transaction() as sess:
        sess["mfa_user_id"] = uid
    resp = client.get("/auth/mfa/verify")
    assert email.encode() not in resp.data
    assert mask_email(email).encode() in resp.data
