from werkzeug.security import generate_password_hash


def _create_user(app, username="user1", email="u1@example.com"):
    from app import db, User
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(username=username, email=email, status="approved")
            user.password_hash = generate_password_hash("oldpass")
            db.session.add(user)
            db.session.commit()
    return user


def test_forgot_password_message_same(client, app):
    _create_user(app)
    app.email_service.send_mail = lambda *a, **k: "msg"
    resp1 = client.post("/auth/forgot", data={"identifier": "u1@example.com"}, follow_redirects=True)
    resp2 = client.post("/auth/forgot", data={"identifier": "nope@example.com"}, follow_redirects=True)
    assert b"verification code has been sent" in resp1.data
    assert b"verification code has been sent" in resp2.data


def test_forgot_password_flow(client, app, monkeypatch):
    user = _create_user(app)
    monkeypatch.setattr("auth.forgot._generate_code", lambda: "123456")
    app.email_service.send_mail = lambda *a, **k: "msg"
    client.post("/auth/forgot", data={"identifier": "u1@example.com"}, follow_redirects=True)
    client.post("/auth/forgot/verify", data={"code": "123456"}, follow_redirects=True)
    client.post(
        "/auth/forgot/reset",
        data={"password": "Newpass1!", "confirm": "Newpass1!"},
        follow_redirects=True,
    )
    from app import User
    with app.app_context():
        updated = User.query.filter_by(email="u1@example.com").first()
        assert updated is not None and updated.check_password("Newpass1!")


def test_no_auto_login_after_reset(client, app, monkeypatch):
    user = _create_user(app)
    monkeypatch.setattr("auth.forgot._generate_code", lambda: "123456")
    app.email_service.send_mail = lambda *a, **k: "msg"
    client.post("/auth/forgot", data={"identifier": "u1@example.com"}, follow_redirects=True)
    client.post("/auth/forgot/verify", data={"code": "123456"}, follow_redirects=True)
    resp = client.post(
        "/auth/forgot/reset",
        data={"password": "Newpass1!", "confirm": "Newpass1!"},
    )
    assert resp.status_code == 302
    assert "/auth/login" in resp.headers["Location"]


def test_resend_cooldown(client, app, monkeypatch):
    _create_user(app)
    app.email_service.send_mail = lambda *a, **k: "msg"
    monkeypatch.setattr("auth.forgot._generate_code", lambda: "654321")
    client.post("/auth/forgot", data={"identifier": "u1@example.com"}, follow_redirects=True)
    resp = client.post("/auth/forgot/resend", follow_redirects=True)
    assert b"Please wait" in resp.data


def test_attempts_exhausted(client, app, monkeypatch):
    _create_user(app)
    app.email_service.send_mail = lambda *a, **k: "msg"
    monkeypatch.setattr("auth.forgot._generate_code", lambda: "222222")
    client.post("/auth/forgot", data={"identifier": "u1@example.com"}, follow_redirects=True)
    for _ in range(5):
        client.post("/auth/forgot/verify", data={"code": "000000"}, follow_redirects=True)
    resp = client.post("/auth/forgot/verify", data={"code": "000000"}, follow_redirects=True)
    assert b"Too many attempts" in resp.data
