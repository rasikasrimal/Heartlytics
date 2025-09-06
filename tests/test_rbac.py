import pytest
from flask import url_for


@pytest.fixture
def login(client):
    from werkzeug.security import generate_password_hash
    from app import db, User

    def _login(role: str):
        email = f"{role.lower()}@example.com"
        with client.application.app_context():
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(username=role.lower(), email=email, role=role, status="approved")
                db.session.add(user)
            user.password_hash = generate_password_hash("pass")
            db.session.commit()
        client.post(
            "/auth/login",
            data={"identifier": email, "password": "pass"},
            follow_redirects=True,
        )
        return client

    return _login


@pytest.mark.parametrize(
    "role, status",
    [
        ("SuperAdmin", 200),
        ("Admin", 403),
        ("Doctor", 200),
        ("User", 200),
    ],
)
def test_predict_access(login, role, status):
    c = login(role)
    resp = c.get("/predict")
    assert resp.status_code == status


@pytest.mark.parametrize(
    "role, status",
    [
        ("SuperAdmin", 200),
        ("Admin", 403),
        ("Doctor", 200),
        ("User", 403),
    ],
)
def test_batch_access(login, role, status):
    c = login(role)
    resp = c.get("/upload")
    assert resp.status_code == status


@pytest.mark.parametrize(
    "role, status",
    [
        ("SuperAdmin", 200),
        ("Admin", 403),
        ("Doctor", 200),
        ("User", 403),
    ],
)
def test_dashboard_access(login, role, status):
    c = login(role)
    resp = c.get("/dashboard")
    assert resp.status_code == status


@pytest.mark.parametrize(
    "role, status",
    [
        ("SuperAdmin", 200),
        ("Admin", 403),
        ("Doctor", 200),
        ("User", 403),
    ],
)
def test_research_access(login, role, status):
    c = login(role)
    resp = c.get("/research")
    assert resp.status_code == status


@pytest.mark.parametrize(
    "role, shows", [
        ("SuperAdmin", ["Predict", "Batch", "Dashboard", "Research"]),
        ("Admin", []),
        ("Doctor", ["Predict", "Batch", "Dashboard", "Research"]),
        ("User", ["Predict"]),
    ],
)
def test_nav_visibility(login, role, shows):
    c = login(role)
    resp = c.get("/")
    html = resp.get_data(as_text=True)
    for label in ["Predict", "Batch", "Dashboard", "Research"]:
        assert (label in html) == (label in shows)


def test_api_json_denied(login, caplog):
    c = login("Admin")
    caplog.set_level("WARNING")
    resp = c.post("/upload", headers={"Accept": "application/json"})
    assert resp.status_code == 403
    assert resp.json["error"] == "forbidden"
    assert any("RBAC deny" in r.message for r in caplog.records)
