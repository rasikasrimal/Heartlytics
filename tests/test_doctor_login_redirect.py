"""Tests for doctor login redirection."""


def test_doctor_redirect_to_dashboard(client):
    from werkzeug.security import generate_password_hash
    from app import db, User

    # Ensure a doctor user exists
    with client.application.app_context():
        user = User.query.filter_by(username="redirectdoc").first()
        if not user:
            user = User(username="redirectdoc", email="rd@example.com", role="Doctor", status="approved")
            db.session.add(user)
        user.password_hash = generate_password_hash("redirectpass")
        db.session.commit()

    response = client.post(
        "/auth/login",
        data={"username": "redirectdoc", "password": "redirectpass"},
        follow_redirects=False,
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
