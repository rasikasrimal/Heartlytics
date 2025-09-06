# HeartLytics: Secure Role-Based Heart Disease Prediction Web Application

**Author:** HMRS Samaranayaka

**Affiliation:** NSBM Green University, Homagama, Sri Lanka

**Date:** 2025-08-01

**Repository Commit:** dcc7a3623f37a4b69d4b0f97a041af07ac757147 (2025-09-06)

## Abstract
HeartLytics is a full-stack Flask platform that predicts heart disease risk while enforcing strict security, encryption, and user-experience guarantees. The system ingests single records or CSV batches, cleans and analyzes data, executes a trained Random Forest model, and surfaces results through role-aware dashboards and PDF reports. Application-level envelope encryption protects patient identifiers, while Bootstrap 5 theming enables accessible light and dark modes. Extensive tests and a phased project plan demonstrate the feasibility of deploying HeartLytics as a secure clinical decision-support prototype.

[TOC]

## List of Figures
1. Context Diagram – [docs/figures/context.mmd](docs/figures/context.mmd)
2. High-Level Architecture – [docs/figures/architecture.mmd](docs/figures/architecture.mmd)
3. DFD Level 0 – [docs/figures/dfd-level0.mmd](docs/figures/dfd-level0.mmd)
4. DFD Level 1: Predict Workflow – [docs/figures/dfd-level1-predict.mmd](docs/figures/dfd-level1-predict.mmd)
5. ER Diagram – [docs/figures/erd.mmd](docs/figures/erd.mmd)
6. Sequence Diagram: Authentication – [docs/figures/seq-auth.mmd](docs/figures/seq-auth.mmd)
7. Sequence Diagram: CSV Upload – [docs/figures/seq-upload.mmd](docs/figures/seq-upload.mmd)
8. Sequence Diagram: Prediction – [docs/figures/seq-predict.mmd](docs/figures/seq-predict.mmd)
9. Deployment Flow – [docs/figures/deployment.mmd](docs/figures/deployment.mmd)

## List of Tables
1. Complete Test Case Inventory

## 1. Working Topic
A secure role-based web application for heart disease risk prediction that integrates machine learning, application-level encryption, and adaptive UI theming to support clinicians and patients.

## 2. Study Area & Study Objectives
HeartLytics operates in the domain of clinical decision support for cardiovascular risk assessment. The application enables clinicians and patients to submit individual or batch datasets, analyze trends, and generate reports. Functional objectives include accurate model inference, interactive dashboards, user management, and PDF exports. Non-functional objectives include strong encryption, role-based access control, and responsive theming.

## 3. Research Gap
Existing heart disease prediction tools often lack integrated security and theming. Few systems combine envelope encryption with rich UI theming and fine-grained RBAC. HeartLytics addresses these gaps by applying AES-256-GCM encryption with per-record data keys and offering a dark theme with chart transparency.

## 4. Research Problem / Questions
- How can a web application securely handle sensitive patient data while providing predictive analytics?
- What UI mechanisms ensure accessibility across light and dark themes without flash-of-unstyled content?
- How can roles and permissions be enforced server-side to protect modules?

## 5. Research Strategy & Method
HeartLytics follows a design science methodology drawing on Peffers et al. (2007). Data collection uses the UCI Heart Disease dataset. Analysis involves Random Forest modeling with scikit-learn. Qualitative insights come from code reviews and security audits.

## 6. System Overview & Architecture
See Figure 1 for the context diagram and Figure 2 for the high-level architecture. External actors (User, Doctor, Admin, SuperAdmin) interact with the Flask application over HTTP. Services handle prediction, PDF generation, data processing, and encryption. The system stores data in SQLite with optional application-level encryption (Figure 2).

### Deployment View
Figure 9 shows the deployment pipeline: development environment feeds into CI which deploys to production. Environment variables drive configuration and secrets are loaded from the OS environment.

## 7. Data Flow Diagrams
Figures 3 and 4 illustrate the overall data flows and the detailed predict workflow. Input data is validated, encrypted, scored by the model, and stored.

## 8. Data Model & ERD
Figure 5 depicts entities including `user`, `patient`, `prediction`, `audit_log`, `role`, and junction `user_roles`. Field-level encryption columns are suffixed with `_ct`, `_nonce`, `_tag`, `_wrapped_dk`, `_kid`, and `_kver` as documented in [docs/encryption.md](docs/encryption.md).

## 9. Security Architecture
Security controls include session-based authentication, rate limiting, CSRF tokens, security headers, and application-level envelope encryption using AES-256-GCM [docs/security_and_encryption.md](docs/security_and_encryption.md). RBAC roles (SuperAdmin, Admin, Doctor, User) restrict module access. Passwords use Argon2id.

## 10. UI/UX & Theming
Light mode is default with dark mode toggle; preference stored in `localStorage` and `theme` cookie for server-side rendering [docs/ui-theming.md](docs/ui-theming.md). Charts auto-adjust colors and backgrounds. Cleaning logs strip blank lines and tables inherit theme-specific styles.

## 11. Key Execution Flows
Sequence diagrams (Figures 6–8) detail authentication with theme persistence, CSV upload and cleaning, and prediction scoring.

## 12. Implementation & Configuration
Environment variables in `.env.example` configure database URI, model path, encryption flags, and KMS settings. Secrets like `SECRET_KEY` are loaded from the OS environment.

## 13. Testing & Evaluation
The repository includes pytest suites covering authentication, encryption, dashboards, RBAC, theming, simulations, and upload workflows. Table 1 lists all planned test cases from `TEST_CASES.md`. Full test code is included in Appendix A.

## 14. Timeline & Project Management
The Gantt chart in `gantt_chart.md` schedules planning, development, testing, deployment, and maintenance phases.

## 15. Ethics, Privacy & Compliance
The system stores only necessary personal data, encrypts sensitive fields, and adheres to OWASP recommendations and GDPR considerations [docs/security_and_encryption.md](docs/security_and_encryption.md).

## 16. Results, Discussion & Conclusion
HeartLytics demonstrates that secure, themed, role-based prediction workflows can be delivered in Flask using envelope encryption and Random Forest modeling. Future work includes expanded datasets, additional algorithms, and usability studies.

## 17. References
Peffers, K., Tuunanen, T., Rothenberger, M. A., & Chatterjee, S. (2007). A Design Science Research Methodology for Information Systems Research.

## Appendix A: Full Test Cases
### Planned Test Cases
# Test Cases

## Authentication & Roles
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-001 | Successful login redirects user to dashboard. | Authentication & Roles | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-002 | Rate limiting blocks more than five invalid logins in 15 min. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-003 | Doctor/Admin signup remains pending until approved. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-004 | Pending doctor cannot log in before approval. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-005 | Regular user cannot access `/superadmin`. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-006 | Logout endpoint terminates session. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-007 | Unauthenticated user is redirected to login when accessing dashboard. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-008 | Signup rejects duplicate email addresses. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-009 | Password must include upper, lower, number and special character. | Authentication & Roles | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-040 | Legacy password hashes upgrade to Argon2id on login. | Authentication & Roles | 🔴 High | 🔒 Security | ⏳ Not Run |

## Prediction
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-010 | Submitting valid data returns prediction label, probability, risk band, and confidence. | Prediction | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-011 | Invalid numeric or categorical values show validation errors. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-012 | Patient name exceeding 120 characters is rejected. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-013 | Prediction result can be downloaded as PDF report. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-014 | Submitting when model is missing shows an informative error. | Prediction | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-015 | Model exception returns friendly error message without crashing. | Prediction | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

## Batch Upload & EDA
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-016 | CSV upload cleans data and shows progress. | Batch Upload & EDA | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-017 | Upload with invalid structure is rejected with error message. | Batch Upload & EDA | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-018 | EDA highlights outliers using multiple algorithms. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-019 | EDA payload separates traces for prediction labels. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-020 | EDA payload groups by string target values. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-021 | EDA payload handles dataset without target column. | Batch Upload & EDA | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-022 | Dashboard export creates PDF with KPIs and charts. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

## Encryption
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-041 | Patient data encrypted with envelope scheme when enabled. | Encryption | 🔴 High | 🔒 Security | ⏳ Not Run |

## RBAC
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-050 | Admin role is forbidden from Predict, Batch, Dashboard, Research modules. | RBAC | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-051 | SuperAdmin bypasses all module restrictions. | RBAC | 🔴 High | 🔒 Security | ⏳ Not Run |

## Doctor Dashboard
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-023 | Doctor dashboard lists only doctor’s own patients. | Doctor Dashboard | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-024 | Doctor cannot view other doctors’ patient records. | Doctor Dashboard | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-025 | Patient list is ordered with newest entries first. | Doctor Dashboard | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

## SuperAdmin Management
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-026 | SuperAdmin approves a pending user. | SuperAdmin Management | 🔴 High | 🧪 Functional | ⏳ Not Run |
| TC-027 | SuperAdmin changes user role or status with audit log. | SuperAdmin Management | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-028 | SuperAdmin resets a user password. | SuperAdmin Management | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-029 | Audit log displays administrative actions. | SuperAdmin Management | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-030 | Admin cannot approve non-doctor accounts. | SuperAdmin Management | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-031 | Admin cannot suspend or modify SuperAdmin status. | SuperAdmin Management | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-032 | Dashboard search filters users by username or email. | SuperAdmin Management | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-033 | Dashboard supports sorting users by role, status, or creation date. | SuperAdmin Management | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-034 | SuperAdmin account is hidden from user list. | SuperAdmin Management | 🔴 High | 🔒 Security | ⏳ Not Run |

## User Settings
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-035 | User updates profile information and avatar. | User Settings | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-036 | User changes password successfully. | User Settings | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-037 | Activity log shows recent user actions. | User Settings | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-038 | Avatar upload rejects non-image files. | User Settings | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-039 | Password change with incorrect current password is rejected. | User Settings | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-040 | Profile update with invalid email format is rejected. | User Settings | 🟢 Low | 🧪 Functional | ⏳ Not Run |

## Simulations
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-041 | Simulations page loads without chart until variable selected. | Simulations | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-042 | Simulation shows risk curve after selecting a variable. | Simulations | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-043 | Selecting unsupported variable returns warning message. | Simulations | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

## Research Paper Viewer
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-044 | Research paper renders with sections and figures. | Research Paper Viewer | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-045 | Navigating to non-existent paper returns 404. | Research Paper Viewer | 🟢 Low | 🧪 Functional | ⏳ Not Run |

## Security
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-046 | Submitting POST without CSRF token is rejected. | Security | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-047 | Session times out after inactivity. | Security | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-048 | Multiple failed logins trigger temporary account lock. | Security | 🔴 High | 🔒 Security | ⏳ Not Run |
| TC-049 | User-supplied data is HTML-escaped to prevent XSS. | Security | 🟡 Medium | 🔒 Security | ⏳ Not Run |
| TC-050 | Safe GET and HEAD requests bypass CSRF validation. | Security | 🟢 Low | 🧪 Functional | ⏳ Not Run |

## Regression
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-051 | Batch prediction handles missing `num_major_vessels` values without error. | Batch Upload & EDA | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

## UI & Layout
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-052 | Login page shows branding, helpful links, and responsive design. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-053 | Password field eye icon toggles visibility on login page. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-054 | Identifier field on login page starts empty without displaying "None". | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-055 | Login form disables autofill so fields remain blank. | Authentication & Roles | 🟢 Low | 🧪 Functional | ⏳ Not Run |

## UI Theming
| Test Case ID | Test Case Description | Module | Priority | Test Type | Status |
| --- | --- | --- | --- | --- | --- |
| TC-060 | Theme toggle updates `data-bs-theme`, cookie, and `localStorage` consistently. | UI Theming | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-061 | Server-side rendering respects `theme` cookie to avoid flash of incorrect theme. | UI Theming | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-062 | Charts and table headers render without white backgrounds in dark mode. | UI Theming | 🟡 Medium | 🧪 Functional | ⏳ Not Run |
| TC-063 | Cleaning log output removes blank or whitespace-only lines for compact display. | UI Theming | 🟢 Low | 🧪 Functional | ⏳ Not Run |
| TC-064 | Login and signup pages expose a persistent theme toggle with no flash on first paint. | UI Theming | 🟡 Medium | 🧪 Functional | ⏳ Not Run |

### Test Source Code

#### tests/__init__.py


#### tests/conftest.py

import sys
import types
import pytest
import os
import base64

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
    os.environ.setdefault("DEV_KMS_MASTER_KEY", base64.b64encode(os.urandom(32)).decode())
    os.environ.setdefault("DEV_KMS_IDX_KEY", base64.b64encode(os.urandom(32)).decode())
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

#### tests/test_auth.py

import re


def test_login_fields_blank(client):
    res = client.get('/auth/login')
    html = res.data.decode()
    identifier_input = re.search(r'<input[^>]*name="identifier"[^>]*>', html).group(0)
    password_input = re.search(r'<input[^>]*name="password"[^>]*>', html).group(0)
    assert 'value=' not in identifier_input
    assert 'value=' not in password_input
    assert 'autocomplete="off"' in identifier_input
    assert 'autocomplete="off"' in password_input

#### tests/test_crypto.py

import pytest
from services.crypto import envelope


def test_encrypt_round_trip(app):
    blob = envelope.encrypt_field(b"secret", "t:c|kid|1")
    assert envelope.decrypt_field(blob, "t:c|kid|1") == b"secret"


def test_tamper_detection(app):
    blob = envelope.encrypt_field(b"secret", "t:c|kid|1")
    blob["ciphertext"] = blob["ciphertext"][:-1] + b"x"
    with pytest.raises(Exception):
        envelope.decrypt_field(blob, "t:c|kid|1")


def test_nonce_uniqueness(app):
    nonces = set()
    for _ in range(50):
        blob = envelope.encrypt_field(b"data", "t:c|kid|1")
        assert blob["nonce"] not in nonces
        nonces.add(blob["nonce"])

#### tests/test_dashboard.py

"""Placeholder tests for dashboard views."""

def test_dashboard_page(auth_client):
    response = auth_client.get("/dashboard")
    assert response.status_code == 200

#### tests/test_eda_payload.py

import pandas as pd

from app import build_eda_payload


def test_build_eda_payload_excludes_removed_visuals_with_predictions():
    df = pd.DataFrame(
        {
            "resting_blood_pressure": [120, 130, 140],
            "cholesterol": [200, 210, 220],
            "prediction": [0, 1, 0],
        }
    )
    payload = build_eda_payload(df)
    assert payload["viz"] == {}


def test_build_eda_payload_excludes_removed_visuals_without_target():
    df = pd.DataFrame(
        {
            "resting_blood_pressure": [120, 130, 140],
            "cholesterol": [200, 210, 220],
        }
    )
    payload = build_eda_payload(df)
    assert payload["viz"] == {}


#### tests/test_encrypted_fields.py

from app import db, Patient, User


def test_patient_encryption_round_trip(app):
    app.config["ENCRYPTION_ENABLED"] = True
    with app.app_context():
        user = User(username="u1", email="u1@example.com", role="Doctor", status="approved")
        db.session.add(user)
        db.session.commit()
        p = Patient(entered_by_user_id=user.id)
        p.patient_data = {"foo": "bar"}
        db.session.add(p)
        db.session.commit()
        assert p.patient_data_ct is not None
        assert p.patient_data == {"foo": "bar"}
        # legacy fallback
        app.config["ENCRYPTION_ENABLED"] = False
        app.config["READ_LEGACY_PLAINTEXT"] = True
        assert p.patient_data == {"foo": "bar"}

#### tests/test_passwords.py

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

#### tests/test_predict.py

"""Placeholder tests for prediction features."""

def test_index_route(auth_client):
    response = auth_client.get("/")
    assert response.status_code == 200

#### tests/test_rbac.py

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

#### tests/test_simulations.py

"""Tests for simulations page."""

def test_simulations_page(auth_client):
    resp = auth_client.get("/simulations/")
    assert resp.status_code == 200
    assert b"Prediction Result" not in resp.data

    resp = auth_client.post("/simulations/run", data={"variable": "age"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert "exercise_angina" in data["results"]
    assert data["results"]["exercise_angina"]["variable"] == "age"

#### tests/test_superadmin_dashboard.py

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

#### tests/test_theme.py

def test_theme_cookie_ssr(auth_client):
    resp = auth_client.get('/', headers={'Cookie': 'theme=dark'})
    assert b'data-bs-theme="dark"' in resp.data


def test_theme_default_light(auth_client):
    resp = auth_client.get('/')
    assert b'data-bs-theme="light"' in resp.data

#### tests/test_upload.py

"""Tests for upload workflow."""

import uuid
from pathlib import Path

import numpy as np
import pandas as pd
import pytest


def test_upload_page(auth_client):
    response = auth_client.get("/upload")
    assert response.status_code == 200


@pytest.mark.parametrize(
    "missing_column, attr",
    [
        ("fasting_blood_sugar", "fasting_blood_sugar"),
        ("exercise_induced_angina", "exercise_angina"),
    ],
)
def test_batch_prediction_handles_missing_int_fields(auth_client, missing_column, attr):
    uid = uuid.uuid4().hex
    uploads_base = Path(auth_client.application.instance_path) / "uploads" / uid
    uploads_base.mkdir(parents=True, exist_ok=True)
    data = {
        "age": [63],
        "sex": [1],
        "chest_pain_type": ["typical_angina"],
        "resting_blood_pressure": [145.0],
        "cholesterol": [233.0],
        "fasting_blood_sugar": [0],
        "Restecg": ["normal"],
        "max_heart_rate_achieved": [150.0],
        "exercise_induced_angina": [0],
        "st_depression": [2.3],
        "st_slope_type": ["upsloping"],
        "num_major_vessels": [0],
        "thalassemia_type": ["normal"],
    }
    data[missing_column] = [np.nan]
    df = pd.DataFrame(data)
    df.to_csv(uploads_base / "clean.csv", index=False)
    with auth_client.application.app_context():
        from app import Prediction, db
        before = Prediction.query.count()
    response = auth_client.post(f"/upload/{uid}/predict")
    assert response.status_code == 200
    with auth_client.application.app_context():
        from app import Prediction
        after = Prediction.query.count()
        assert after == before + 1
        pred = Prediction.query.order_by(Prediction.id.desc()).first()
        assert getattr(pred, attr) is None
