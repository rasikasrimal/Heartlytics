"""Tests for SuperAdmin dashboard safeguards."""

def create_doctor(app, username="doc"):
    from app import db, User
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User(
                username=username,
                email=f"{username}@example.com",
                role="Doctor",
                status="approved",
            )
            db.session.add(user)
            db.session.commit()
        return user


def test_superadmin_not_listed(superadmin_client):
    # ensure another user exists
    create_doctor(superadmin_client.application)
    resp = superadmin_client.get("/superadmin/")
    assert resp.status_code == 200
    assert b"doc" in resp.data
    # SuperAdmin should not appear in the user listing table
    assert b"<td>superadmin</td>" not in resp.data


def test_superadmin_cannot_suspend_self(superadmin_client):
    from app import db, User
    with superadmin_client.application.app_context():
        sa = User.query.filter_by(username="superadmin").first()
        sa_id = sa.id
    resp = superadmin_client.post(f"/superadmin/users/{sa_id}/status", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Cannot modify SuperAdmin status" in resp.data
    with superadmin_client.application.app_context():
        sa = User.query.get(sa_id)
        assert sa.status == "approved"
