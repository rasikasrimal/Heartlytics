from werkzeug.security import generate_password_hash


def test_password_upgrade_on_login(app, client):
    from app import db, User

    with app.app_context():
        u = User(username="legacyuser", email="l@example.com", role="User", status="approved")
        u.password_hash = generate_password_hash("pass")
        db.session.add(u)
        db.session.commit()

    client.post("/auth/login", data={"identifier": "l@example.com", "password": "pass"}, follow_redirects=True)

    with app.app_context():
        u = User.query.filter_by(username="legacyuser").first()
        assert u.password_hash.startswith("$argon2id$")
