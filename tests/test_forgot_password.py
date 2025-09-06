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
    resp1 = client.post("/auth/forgot", data={"identifier": "u1@example.com"}, follow_redirects=True)
    resp2 = client.post("/auth/forgot", data={"identifier": "nope@example.com"}, follow_redirects=True)
    assert b"verification code has been sent" in resp1.data
    assert b"verification code has been sent" in resp2.data


def test_forgot_password_flow(client, app, monkeypatch):
    user = _create_user(app)
    monkeypatch.setattr("secrets.randbelow", lambda n: 123456)
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
