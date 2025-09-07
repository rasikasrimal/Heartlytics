from werkzeug.security import generate_password_hash
from datetime import datetime


def test_password_upgrade_on_login(app, client):
    from app import db, User

    with app.app_context():
        User.query.filter_by(email="l@example.com").delete()
        db.session.commit()
        u = User(username="legacyuser", email="l@example.com", role="User", status="approved")
        u.password_hash = generate_password_hash("pass")
        u.email_verified_at = datetime.utcnow()
        db.session.add(u)
        db.session.commit()

    client.post("/auth/login", data={"identifier": "l@example.com", "password": "pass"}, follow_redirects=True)

    with app.app_context():
        u = User.query.filter_by(username="legacyuser").first()
        assert u.password_hash.startswith("$argon2id$")
