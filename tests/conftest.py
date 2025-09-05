import sys
import types
import pytest

# Provide a minimal stub for `python-dotenv` if the package isn't installed.
# This avoids import errors during tests when the optional dependency is missing.
if "dotenv" not in sys.modules:  # pragma: no cover - simple import guard
    dotenv_stub = types.ModuleType("dotenv")
    dotenv_stub.load_dotenv = lambda *args, **kwargs: None
    sys.modules["dotenv"] = dotenv_stub

# scikit-learn's IterativeImputer lives behind an experimental flag.
# Importing this module enables it so the main app can import without errors.
try:  # pragma: no cover - best effort
    import sklearn.experimental.enable_iterative_imputer  # type: ignore  # noqa: F401
except Exception:
    pass

@pytest.fixture
def app():
    """Create and configure a Flask app for tests."""
    try:
        from app import create_app  # type: ignore
    except Exception:
        create_app = None
    if create_app:
        flask_app = create_app()
    else:
        from app import app as flask_app  # type: ignore
    # Ensure the secrets module is available in the app namespace for CSRF token generation.
    import app as app_module  # type: ignore
    import secrets as _secrets
    app_module.secrets = _secrets
    flask_app.config.update({"TESTING": True, "WTF_CSRF_ENABLED": False})
    yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """Return a test client logged in as a default doctor user."""
    from werkzeug.security import generate_password_hash
    from app import db, User

    with client.application.app_context():
        user = User.query.filter_by(username="tester").first()
        if not user:
            user = User(username="tester", email="t@example.com", role="Doctor", status="approved")
            db.session.add(user)
        user.password_hash = generate_password_hash("testpass")
        db.session.commit()

    client.post(
        "/auth/login",
        data={"identifier": "t@example.com", "password": "testpass"},
        follow_redirects=True,
    )
    return client


@pytest.fixture
def superadmin_client(client):
    """Return a test client logged in as a SuperAdmin user."""
    from werkzeug.security import generate_password_hash
    from app import db, User

    with client.application.app_context():
        user = User.query.filter_by(username="superadmin").first()
        if not user:
            user = User(
                username="superadmin",
                email="sa@example.com",
                role="SuperAdmin",
                status="approved",
            )
            db.session.add(user)
        user.password_hash = generate_password_hash("sapass")
        db.session.commit()

    client.post(
        "/auth/login",
        data={"identifier": "superadmin", "password": "sapass"},
        follow_redirects=True,
    )
    return client
