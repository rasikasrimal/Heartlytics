from __future__ import annotations


# ============================
# Heart Disease Risk App + CSV Upload/EDA/Batch Predict
# ============================

import os
import io
import json
import uuid
import pickle
import math
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
import re
from flask import (
    Flask, render_template, request, redirect, url_for, flash, jsonify,
    send_file, session, abort
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from config import DevelopmentConfig, ProductionConfig

# ML imputation helpers
from sklearn.metrics import (
    silhouette_score,
    confusion_matrix,
)
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.cluster import KMeans

from outlier_detection import (
    combine_outlier_reports,
    OUTLIER_METHODS,
    run_outlier_methods,
)

from services.auth import role_required
from services.pdf import generate_prediction_pdf
from services.data import (
    INPUT_COLUMNS,
    NUMERIC_COLS,
    CATEGORICAL_COLS,
    COLUMN_ALIASES,
    REQUIRED_INTERNAL_COLUMNS,
    OPTIONAL_KEEP,
    NUMERIC_FEATURES_INT,
    NUMERIC_FEATURES_FLOAT,
    BINARY_FEATURES,
    CATEGORICAL_FEATURES,
    group_cleaning_log,
    clean_dataframe,
    find_optional_in_raw,
    normalize_columns,
    validate_structure,
)
from services.security import (
    csrf_protect,
    get_csrf_token,
    csrf_protect_api,
)

from sqlalchemy import inspect, text

# ---------------------------
# App & Config
# ---------------------------
app = Flask(__name__, instance_relative_config=True)
env = os.getenv("FLASK_ENV", "production")
app.config.from_object(DevelopmentConfig if env == "development" else ProductionConfig)

# Session configuration
login_manager = LoginManager(app)
login_manager.login_view = "auth.login"
app.permanent_session_lifetime = timedelta(minutes=30)

# Ensure instance dir
os.makedirs(app.instance_path, exist_ok=True)

# uploads dir (under instance/)
UPLOADS_DIR = os.path.join(app.instance_path, "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

# avatar uploads
AVATAR_DIR = app.config.get("AVATAR_UPLOAD_FOLDER")
os.makedirs(AVATAR_DIR, exist_ok=True)
ALLOWED_AVATAR_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app.config["ALLOWED_AVATAR_EXTENSIONS"] = ALLOWED_AVATAR_EXTENSIONS

# Security headers
@app.after_request
def set_security_headers(resp):
    resp.headers['X-Content-Type-Options'] = 'nosniff'
    resp.headers['X-Frame-Options'] = 'DENY'
    resp.headers['Referrer-Policy'] = 'no-referrer'
    resp.headers['Permissions-Policy'] = 'interest-cohort=()'
    return resp

# Restrict regular users to prediction functionality only
@app.before_request
def limit_user_pages():
    if current_user.is_authenticated and getattr(current_user, "role", None) == "User":
        allowed = {
            "index",
            "predict.predict_page",
            "predict.predict",
            "auth.logout",
            "settings.settings",
        }
        if request.endpoint not in allowed and not (request.endpoint or "").startswith("static"):
            return abort(403)

# Jinja helpers
app.jinja_env.globals.update(zip=zip)
SEX_MAP = {0: "Female", 1: "Male"}
YESNO = {0: "No", 1: "Yes"}
UNITS = {
    "resting_bp": "mmHg",
    "cholesterol": "mg/dL",
    "max_heart_rate": "bpm",
    "oldpeak": "",
    "num_major_vessels": ""
}
app.jinja_env.globals.update(SEX_MAP=SEX_MAP, YESNO=YESNO, UNITS=UNITS)


def load_research_paper(path: str = "research_paper.tex") -> dict:
    """Parse the LaTeX manuscript into structured HTML-friendly data."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.abspath(os.path.join(base_dir, path))
    # Ensure requested file resides within the application directory
    try:
        if os.path.commonpath([base_dir, full_path]) != base_dir:
            return {}
    except ValueError:
        return {}
    try:
        with open(full_path, encoding="utf-8") as f:

            tex = f.read()
    except OSError:
        return {}

    try:
        from pylatexenc.latex2text import LatexNodes2Text
    except ModuleNotFoundError:
        return {}

    # Build reference map
    bibitems = {}
    for key, body in re.findall(r"\\bibitem\{(.*?)\}(.*?)(?=\\bibitem|\\end\{thebibliography\})", tex, re.DOTALL):
        bibitems[key.strip()] = LatexNodes2Text(math_mode='verbatim').latex_to_text(body).strip()
    ref_index = {k: str(i + 1) for i, k in enumerate(bibitems.keys())}

    def replace_cites(text: str) -> str:
        def repl(m):
            keys = [k.strip() for k in m.group(1).split(',')]
            nums = [ref_index.get(k, '?') for k in keys]
            return '[' + ','.join(nums) + ']'
        return re.sub(r"\\cite\{([^}]+)\}", repl, text)

    def to_html(s: str) -> str:
        s = replace_cites(s)
        # lists
        def enum_repl(m):
            items = re.findall(r"\\item\s+(.*?)(?=\\item|\\end\{enumerate\})", m.group(0), re.DOTALL)
            lis = ''.join(f"<li>{to_html(i.strip())}</li>" for i in items)
            return f"<ol>{lis}</ol>"
        s = re.sub(r"\\begin\{enumerate\}.*?\\end\{enumerate\}", enum_repl, s, flags=re.DOTALL)
        # line breaks
        s = s.replace('\\\n', '<br>')
        txt = LatexNodes2Text(math_mode='verbatim').latex_to_text(s)
        return txt.strip()

    title = LatexNodes2Text().latex_to_text(re.search(r"\\title\{(.*?)\}", tex, re.DOTALL).group(1)).strip()
    auth = re.search(r"\\IEEEauthorblockN\{(.*?)\}\s*\\IEEEauthorblockA\{(.*?)\}", tex, re.DOTALL)
    author = affiliation = ""
    if auth:
        author = LatexNodes2Text().latex_to_text(auth.group(1)).strip()
        affiliation = LatexNodes2Text().latex_to_text(auth.group(2).replace('\\', ', ')).strip()

    abstract = to_html(re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.DOTALL).group(1))
    keywords = to_html(re.search(r"\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}", tex, re.DOTALL).group(1))

    sections = []
    for title_s, body in re.findall(r"\\section\{(.*?)\}(.*?)(?=\\section\{|\\begin\{thebibliography\}|\\appendices|\\end\{document\})", tex, re.DOTALL):
        sections.append({"title": LatexNodes2Text().latex_to_text(title_s).strip(), "content": to_html(body)})

    figures = []
    for grp in re.findall(r"\\begin\{figure\}.*?\\includegraphics.*?\{([^}]+)\}.*?\\caption\{(.*?)\}.*?\\end\{figure\}", tex, re.DOTALL):
        img, cap = grp
        figures.append({"src": img.strip(), "caption": to_html(cap)})

    tables = []
    for cap, body in re.findall(r"\\begin\{table\}.*?\\caption\{(.*?)\}.*?\\begin\{tabular\}{.*?}(.*?)\\end\{tabular\}.*?\\end\{table\}", tex, re.DOTALL):
        rows = []
        for row in re.split(r"\\\\", body):
            row = row.strip()
            if not row or row in ("\\toprule", "\\midrule", "\\bottomrule"):
                continue
            cells = [to_html(c) for c in row.split("&")]
            rows.append(cells)
        tables.append({"caption": to_html(cap), "rows": rows})

    refs = list(bibitems.values())

    return {
        "title": title,
        "author": author,
        "affiliation": affiliation,
        "abstract": abstract,
        "keywords": keywords,
        "sections": sections,
        "figures": figures,
        "tables": tables,
        "references": refs,
    }

# ---------------------------
# Database
# ---------------------------
db = SQLAlchemy(app)
# Expose the database on the application object so blueprints can
# access it without importing this module again, which would create a
# second Flask application instance when running via ``python app.py``.
app.db = db


class User(db.Model, UserMixin):
    """Application user capable of authenticating via username/email."""

    id = db.Column(db.Integer, primary_key=True)
    # Public facing stable identifier used across the system
    uid = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    username = db.Column(db.String(80), unique=True, nullable=False)
    nickname = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="User")
    status = db.Column(db.String(20), default="pending")
    requested_role = db.Column(db.String(20))
    # Relationship to support many-to-many roles in future-proof design
    roles = db.relationship(
        "Role", secondary="user_roles", backref="users", lazy="dynamic"
    )
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    last_login = db.Column(db.DateTime)
    avatar = db.Column(db.String(255))

    def set_password(self, password: str) -> None:
        """Hash and store the given password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return ``True`` if ``password`` matches the stored hash."""
        return check_password_hash(self.password_hash, password)


class AuditLog(db.Model):
    """Record administrative actions for accountability."""

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    acting_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    target_user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    old_value = db.Column(db.String(120))
    new_value = db.Column(db.String(120))

    acting_user = db.relationship("User", foreign_keys=[acting_user_id])
    target_user = db.relationship("User", foreign_keys=[target_user_id])


class Role(db.Model):
    """Defines a system role with a set of JSON-based permissions."""

    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    permissions = db.Column(db.JSON, nullable=False, default=dict)


# Default system roles and their permissions. These can be extended in future
# without schema changes thanks to the JSON column on :class:`Role`.
DEFAULT_ROLE_PERMISSIONS = {
    "SuperAdmin": {
        "manage_admins": True,
        "manage_doctors": True,
        "view_audit_logs": True,
        "dashboard": "full",
    },
    "Admin": {
        "manage_doctors": True,
        "view_audit_logs": False,
        "dashboard": "stats",
    },
    "Doctor": {
        "enter_patient_data": True,
        "predict_risk": True,
        "view_own_patients": True,
    },
    "User": {
        "enter_patient_data": True,
        "predict_risk": True,
    },
}


class UserRole(db.Model):
    """Association table mapping users to roles (many-to-many)."""

    __tablename__ = "user_roles"

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey("role.id"), primary_key=True)


class Patient(db.Model):
    """Stores patient data and prediction results."""

    id = db.Column(db.Integer, primary_key=True)
    entered_by_user_id = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    patient_data = db.Column(db.JSON, nullable=False)
    prediction_result = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    entered_by = db.relationship("User", backref="patients")

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    patient_name = db.Column(db.String(120))
    age = db.Column(db.Integer, nullable=False)
    sex = db.Column(db.Integer, nullable=False)  # 0/1
    chest_pain_type = db.Column(db.String(50))
    country = db.Column(db.String(50))  # optional (not used by the model)
    resting_bp = db.Column(db.Float)
    cholesterol = db.Column(db.Float)
    fasting_blood_sugar = db.Column(db.Integer)
    resting_ecg = db.Column(db.String(50))
    max_heart_rate = db.Column(db.Float)
    exercise_angina = db.Column(db.Integer)
    oldpeak = db.Column(db.Float)
    st_slope = db.Column(db.String(50))
    num_major_vessels = db.Column(db.Integer)
    thalassemia_type = db.Column(db.String(50))
    prediction = db.Column(db.Integer, nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    model_version = db.Column(db.String(120))
    cluster_id = db.Column(db.Integer)

    def to_dict(self):
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat(),
            "age": self.age,
            "sex": self.sex,
            "chest_pain_type": self.chest_pain_type,
            "country": self.country,
            "resting_blood_pressure": self.resting_bp,
            "cholesterol": self.cholesterol,
            "fasting_blood_sugar": self.fasting_blood_sugar,
            "Restecg": self.resting_ecg,
            "max_heart_rate_achieved": self.max_heart_rate,
            "exercise_induced_angina": self.exercise_angina,
            "st_depression": self.oldpeak,
            "st_slope_type": self.st_slope,
            "num_major_vessels": self.num_major_vessels,
            "thalassemia_type": self.thalassemia_type,
            "prediction": self.prediction,
            "confidence": self.confidence,
            "model_version": self.model_version,
            "cluster_id": self.cluster_id,
        }

# Summary stats for clusters
class ClusterSummary(db.Model):
    cluster_id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer)
    avg_age = db.Column(db.Float)
    avg_cholesterol = db.Column(db.Float)
    avg_resting_blood_pressure = db.Column(db.Float)
    avg_st_depression = db.Column(db.Float)
    avg_risk_pct = db.Column(db.Float)
    pct_male = db.Column(db.Float)
    pct_female = db.Column(db.Float)
    common_chest_pain_type = db.Column(db.String(50))
    common_thalassemia_type = db.Column(db.String(50))

    def to_dict(self):
        return {
            "cluster_id": self.cluster_id,
            "count": self.count,
            "avg_age": self.avg_age,
            "avg_cholesterol": self.avg_cholesterol,
            "avg_resting_blood_pressure": self.avg_resting_blood_pressure,
            "avg_st_depression": self.avg_st_depression,
            "avg_risk_pct": self.avg_risk_pct,
            "pct_male": self.pct_male,
            "pct_female": self.pct_female,
            "common_chest_pain_type": self.common_chest_pain_type,
            "common_thalassemia_type": self.common_thalassemia_type,
        }

# Make models available via the application object for easier access in
# blueprints without re-importing this module.
app.User = User
app.Prediction = Prediction
app.ClusterSummary = ClusterSummary
app.AuditLog = AuditLog
app.Role = Role
app.UserRole = UserRole
app.Patient = Patient


@login_manager.user_loader
def load_user(user_id: str):
    """Return the :class:`User` instance for the given ``user_id``."""
    return User.query.get(int(user_id))


@app.before_request
def enforce_session_timeout():
    """Log out users after a period of inactivity."""
    if not current_user.is_authenticated:
        return
    now = datetime.utcnow()
    last = session.get("last_active")
    if last and now - datetime.fromisoformat(last) > app.permanent_session_lifetime:
        logout_user()
        flash("Session expired, please log in again.", "warning")
        return redirect(url_for("auth.login"))
    session["last_active"] = now.isoformat()


@app.errorhandler(403)
def forbidden(_):
    """Render a user-friendly forbidden page."""
    return (
        render_template(
            "error.html",
            title="Forbidden",
            message="Access denied. You do not have permission to view this page.",
        ),
        403,
    )

with app.app_context():
    db.create_all()
    insp = inspect(db.engine)

    # ensure cluster_id column exists for older databases
    pred_cols = [c["name"] for c in insp.get_columns("prediction")]
    if "cluster_id" not in pred_cols:
        db.session.execute(text("ALTER TABLE prediction ADD COLUMN cluster_id INTEGER"))
        db.session.commit()

    # ensure uid, requested_role and updated_at columns exist for existing user tables
    user_cols = [c["name"] for c in insp.get_columns("user")]
    if "requested_role" not in user_cols:
        db.session.execute(
            text("ALTER TABLE user ADD COLUMN requested_role VARCHAR(20)")
        )
        db.session.commit()
    if "uid" not in user_cols:
        db.session.execute(text("ALTER TABLE user ADD COLUMN uid VARCHAR(36)"))
        db.session.commit()
        for u in db.session.query(User).all():
            u.uid = str(uuid.uuid4())
        db.session.commit()
        db.session.execute(
            text("CREATE UNIQUE INDEX IF NOT EXISTS ix_user_uid ON user (uid)")
        )
        db.session.commit()
    if "updated_at" not in user_cols:
        db.session.execute(text("ALTER TABLE user ADD COLUMN updated_at DATETIME"))
        db.session.commit()
        db.session.execute(
            text(
                "UPDATE user SET updated_at = COALESCE(created_at, CURRENT_TIMESTAMP)"
            )
        )
        db.session.commit()
    if "avatar" not in user_cols:
        db.session.execute(text("ALTER TABLE user ADD COLUMN avatar VARCHAR(255)"))
        db.session.commit()
    if "nickname" not in user_cols:
        db.session.execute(text("ALTER TABLE user ADD COLUMN nickname VARCHAR(80)"))
        db.session.commit()
        db.session.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS ix_user_nickname ON user (nickname) WHERE nickname IS NOT NULL"
            )
        )
        db.session.commit()

    # ensure default roles are present
    for name, perms in DEFAULT_ROLE_PERMISSIONS.items():
        if not Role.query.filter_by(role_name=name).first():
            db.session.add(Role(role_name=name, permissions=perms))
    db.session.commit()

    # seed a default Super Admin if none exists
    if not User.query.filter_by(role="SuperAdmin").first():
        sa = User(
            username="admin",
            email="admin@example.com",
            role="SuperAdmin",
            status="approved",
            created_at=datetime.utcnow(),
        )
        sa.set_password("admin")
        sa_role = Role.query.filter_by(role_name="SuperAdmin").first()
        if sa_role:
            sa.roles.append(sa_role)
        db.session.add(sa)
        db.session.commit()


def run_kmeans():
    rows = Prediction.query.all()
    if len(rows) < 3:
        return

    data = [r.to_dict() for r in rows]
    df = pd.DataFrame(data)
    df["risk_pct"] = df.apply(
        lambda r: (r["confidence"] if r["prediction"] == 1 else 1 - r["confidence"]) * 100,
        axis=1,
    )

    numeric = [
        "age",
        "cholesterol",
        "resting_blood_pressure",
        "max_heart_rate_achieved",
        "st_depression",
        "num_major_vessels",
        "risk_pct",
    ]
    categorical = [
        "sex",
        "chest_pain_type",
        "st_slope_type",
        "thalassemia_type",
        "exercise_induced_angina",
        "fasting_blood_sugar",
    ]

    X_num = df[numeric]
    X_cat = df[categorical]

    try:
        enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    except TypeError:  # for older scikit-learn
        enc = OneHotEncoder(sparse=False, handle_unknown="ignore")
    X_cat_enc = enc.fit_transform(X_cat)
    scaler = StandardScaler()
    X_num_scaled = scaler.fit_transform(X_num)
    X = np.hstack([X_num_scaled, X_cat_enc])

    enc_path = os.path.join(app.instance_path, "cluster_encoder.pkl")
    scaler_path = os.path.join(app.instance_path, "cluster_scaler.pkl")
    with open(enc_path, "wb") as f:
        pickle.dump(enc, f)
    with open(scaler_path, "wb") as f:
        pickle.dump(scaler, f)

    best_score = -1
    best_labels = None
    for k in [3, 4, 5]:
        if len(df) <= k:
            continue
        km = KMeans(n_clusters=k, n_init=10, random_state=0)
        labels = km.fit_predict(X)
        score = silhouette_score(X, labels)
        if score > best_score:
            best_score = score
            best_labels = labels
    if best_labels is None:
        return

    df["cluster_id"] = best_labels
    for row, cid in zip(rows, df["cluster_id"]):
        row.cluster_id = int(cid)
    db.session.commit()

    ClusterSummary.query.delete()
    db.session.commit()
    for cid in sorted(df["cluster_id"].unique()):
        sub = df[df["cluster_id"] == cid]
        summary = ClusterSummary(
            cluster_id=int(cid),
            count=len(sub),
            avg_age=sub["age"].mean(),
            avg_cholesterol=sub["cholesterol"].mean(),
            avg_resting_blood_pressure=sub["resting_blood_pressure"].mean(),
            avg_st_depression=sub["st_depression"].mean(),
            avg_risk_pct=sub["risk_pct"].mean(),
            pct_male=(sub["sex"] == 1).mean() * 100,
            pct_female=(sub["sex"] == 0).mean() * 100,
            common_chest_pain_type=sub["chest_pain_type"].mode().iat[0] if not sub["chest_pain_type"].mode().empty else "",
            common_thalassemia_type=sub["thalassemia_type"].mode().iat[0] if not sub["thalassemia_type"].mode().empty else "",
        )
        db.session.add(summary)
    db.session.commit()


@app.get("/api/kmeans")
@login_required
def api_kmeans():
    """Run K-Means clustering on selected features and return cluster info."""
    rows = Prediction.query.all()
    if not rows:
        return jsonify({"labels": {}, "summaries": [], "silhouette": None})

    allowed = {
        "age",
        "cholesterol",
        "resting_blood_pressure",
        "max_heart_rate_achieved",
        "st_depression",
        "num_major_vessels",
        "risk_pct",
    }
    feats_param = request.args.get("features", "")
    features = [f for f in feats_param.split(",") if f in allowed]
    if len(features) < 2:
        return jsonify({"error": "select at least two features"}), 400

    k_param = request.args.get("k", "3")
    if not k_param.isdigit():
        return jsonify({"error": "k must be a positive integer"}), 400
    k = int(k_param)
    if k < 2:
        k = 2

    data = [r.to_dict() for r in rows]
    df = pd.DataFrame(data)
    df["risk_pct"] = df.apply(
        lambda r: (r["confidence"] if r["prediction"] == 1 else 1 - r["confidence"]) * 100,
        axis=1,
    )
    df_feat = df[features].dropna()
    if len(df_feat) <= k:
        return jsonify({"error": "not enough data"}), 400

    scaler = StandardScaler()
    X = scaler.fit_transform(df_feat)
    km = KMeans(n_clusters=k, n_init=10, max_iter=300, random_state=0)
    labels = km.fit_predict(X)
    centers = scaler.inverse_transform(km.cluster_centers_)

    df.loc[df_feat.index, "cluster_id"] = labels
    summaries = []
    for cid in range(k):
        idxs = df_feat.index[labels == cid]
        sub = df.loc[idxs]
        centroid_vals = {feat: float(centers[cid, i]) for i, feat in enumerate(features)}
        summaries.append(
            {
                "cluster_id": int(cid),
                "avg_age": sub["age"].mean(),
                "avg_cholesterol": sub["cholesterol"].mean(),
                "avg_risk_pct": sub["risk_pct"].mean(),
                "common_chest_pain_type": sub["chest_pain_type"].mode().iat[0]
                if not sub["chest_pain_type"].mode().empty
                else "",
                "common_thalassemia_type": sub["thalassemia_type"].mode().iat[0]
                if not sub["thalassemia_type"].mode().empty
                else "",
                "centroid": centroid_vals,
            }
        )

    labels_map = {int(df.loc[i, "id"]): int(df.loc[i, "cluster_id"]) for i in df_feat.index}
    sil = None
    if k > 1 and len(df_feat) > k:
        sil = float(silhouette_score(X, labels))

    return jsonify({"labels": labels_map, "summaries": summaries, "silhouette": sil})

# ---------------------------
# Model File
# ---------------------------
MODEL_PATH = app.config["MODEL_PATH"]
if not os.path.exists(MODEL_PATH):
    print("model.pkl not found at", MODEL_PATH)

def load_model(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)

model = load_model(MODEL_PATH) if os.path.exists(MODEL_PATH) else None
model_name = os.path.basename(MODEL_PATH)
# Expose model info on the app for blueprint access without importing
# this module again.
app.model = model
app.model_name = model_name

# ---------------------------
# Training Schema (exact columns used by model)
# ---------------------------
# NOTE: country REMOVED from features
# ---------------------------

app.jinja_env.globals['csrf_token'] = get_csrf_token

from routes.predict import predict_bp
from auth import auth_bp
from superadmin import superadmin_bp
from doctor import doctor_bp
from user import user_bp
from routes.settings import settings_bp

app.register_blueprint(predict_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(superadmin_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(user_bp)
app.register_blueprint(settings_bp)


@app.route("/admin/")
@login_required
@role_required(["Admin", "SuperAdmin"])
def admin_dashboard_alias():
    """Redirect legacy /admin/ path to unified dashboard."""
    return redirect(url_for("superadmin.dashboard"))

@app.delete("/api/predictions/<int:pid>")
@login_required
@csrf_protect_api
def api_delete_prediction(pid: int):
    pred = Prediction.query.get(pid)
    if not pred:
        return jsonify({"ok": False, "error": "Not found"}), 404
    try:
        db.session.delete(pred)
        db.session.commit()
        return jsonify({"ok": True, "id": pid})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500

@app.post("/api/predictions/<int:pid>/delete")
@login_required
@csrf_protect_api
def api_delete_prediction_legacy(pid: int):
    pred = Prediction.query.get(pid)
    if not pred:
        return jsonify({"ok": False, "error": "Not found"}), 404
    try:
        db.session.delete(pred)
        db.session.commit()
        return jsonify({"ok": True, "id": pid})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500

@app.delete("/api/predictions")
@login_required
@csrf_protect_api
def api_delete_all_predictions():
    try:
        deleted = Prediction.query.delete()
        db.session.commit()
        return jsonify({"ok": True, "deleted": deleted})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500


@app.delete("/api/outliers")
@login_required
@csrf_protect_api
def api_delete_outliers():
    try:
        ids = request.get_json(force=True).get("ids", [])
    except Exception:
        ids = []
    if not ids:
        return jsonify({"ok": False, "error": "No ids provided"}), 400
    try:
        deleted = Prediction.query.filter(Prediction.id.in_(ids)).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({"ok": True, "deleted": deleted})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 500

# ---------------------------
# Pages
# ---------------------------
@app.get("/")
@login_required
def index():
    defaults = {
        "patient_name": "Demo Patient",
        "age": 63,
        "sex": 1,
        "chest_pain_type": "typical_angina",
        "country": "Cleveland",  # optional, for display/reporting only
        "resting_blood_pressure": 145.0,
        "cholesterol": 233.0,
        "fasting_blood_sugar": 1,
        "Restecg": "left_ventricular_hypertrophy",
        "max_heart_rate_achieved": 150.0,
        "exercise_induced_angina": 0,
        "st_depression": 2.3,
        "st_slope_type": "downsloping",
        "num_major_vessels": 0,
        "thalassemia_type": "fixed_defect",
    }
    return render_template("predict/form.html", defaults=defaults, model_name=model_name, theme="dark")


# ---------------------------
# Dashboard
# ---------------------------
@app.get("/dashboard")
@login_required
def dashboard():
    rows = Prediction.query.order_by(Prediction.created_at.asc()).all()
    data = [r.to_dict() for r in rows]
    return render_template(
        "dashboard/index.html",
        data=data,
        clusters=[],
    )


@app.route("/outliers", methods=["GET", "POST"])
@login_required
def outlier_handling():
    """Interactive page to run and compare multiple outlier detectors."""
    rows = Prediction.query.order_by(Prediction.created_at.asc()).all()
    data = [r.to_dict() for r in rows]
    selected = request.form.getlist("methods")
    results = {}
    if selected and data:
        df = pd.DataFrame(data)
        res = run_outlier_methods(df, selected)
        for key, val in res.items():
            val["rows"] = val["rows"].drop(columns=["patient_name"], errors="ignore").to_dict(orient="records")
        results = res
    methods = {k: v[0] for k, v in OUTLIER_METHODS.items()}
    return render_template(
        "dashboard/outliers.html",
        methods=methods,
        selected=selected,
        results=results,
    )


@app.get("/dashboard/pdf")
@login_required
def dashboard_pdf():
    """Render PDF generation options page with preview data."""
    rows = Prediction.query.order_by(Prediction.created_at.asc()).all()
    data = [
        {
            "id": r.id,
            "age": r.age,
            "sex": SEX_MAP.get(r.sex, r.sex),
            "chest_pain": r.chest_pain_type,
            "rest_bp": r.resting_bp,
            "cholesterol": r.cholesterol,
            "max_hr": r.max_heart_rate,
            "prediction": r.prediction,
            "pred_label": "Yes" if r.prediction else "No",

            "risk_pct": (r.confidence if r.prediction == 1 else 1 - r.confidence) * 100,
            "date": r.created_at.isoformat(),
        }
        for r in rows
    ]
    min_date = data[0]["date"][:10] if data else datetime.now().strftime("%Y-%m-%d")
    max_date = data[-1]["date"][:10] if data else datetime.now().strftime("%Y-%m-%d")
    return render_template("dashboard/pdf.html", records=data, min_date=min_date, max_date=max_date)



@app.post("/dashboard/pdf")
@login_required
def dashboard_pdf_generate():
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        Image,
        PageBreak,
    )
    from reportlab.lib.styles import getSampleStyleSheet
    import pandas as pd
    import os
    
    include_patient = True
    include_inputs = True
    include_results = True
    include_visuals = True
    notes = request.form.get("doctor_notes", "").strip()
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    min_pct = float(request.form.get("min_pct", 0) or 0)
    max_pct = float(request.form.get("max_pct", 100) or 100)
    genders = request.form.getlist("gender")
    diseases = request.form.getlist("disease")
    sort_by = request.form.get("sort_by", "id")
    where_clause = request.form.get("custom_where", "").strip()
    columns = request.form.get("columns", "")
    if columns:
        columns = [c for c in columns.split(",") if c]
    else:
        columns = [
            "id",
            "age",
            "sex",
            "chest_pain",
            "rest_bp",
            "cholesterol",
            "max_hr",
            "pred_label",
            "risk_pct",
        ]

    # PDF theme selection was removed from the UI, but some deployments may still
    # send a `theme` field. Default to light theme to avoid NameError on access.
    theme = request.form.get("theme", "light")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        plt = None
    try:
        import seaborn as sns
    except ModuleNotFoundError:
        sns = None
    if plt is not None:
        plt.rcParams.update(
            {
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "axes.edgecolor": "#e0e0e0",
                "axes.grid": True,
                "grid.color": "#e0e0e0",
                "axes.labelcolor": "#111111",
                "xtick.color": "#111111",
                "ytick.color": "#111111",
                "text.color": "#111111",
                "font.family": "DejaVu Sans",
            }
        )
        if theme == "dark":
            plt.rcParams.update(
                {
                    "figure.facecolor": "#222222",
                    "axes.facecolor": "#222222",
                    "axes.labelcolor": "#eeeeee",
                    "xtick.color": "#eeeeee",
                    "ytick.color": "#eeeeee",
                    "text.color": "#eeeeee",
                    "grid.color": "#444444",
                }
            )
    if sns is not None:
        if theme == "dark":
            sns.set_theme(
                style="darkgrid",
                rc={
                    "axes.facecolor": "#222222",
                    "axes.edgecolor": "#444444",
                    "grid.color": "#444444",
                },
            )
        else:
            sns.set_theme(
                style="whitegrid",
                rc={
                    "axes.facecolor": "white",
                    "axes.edgecolor": "#e0e0e0",
                    "grid.color": "#e0e0e0",
                },
            )
    import numpy as np

    query = Prediction.query
    if start_date:
        query = query.filter(Prediction.created_at >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(
            Prediction.created_at <= datetime.fromisoformat(end_date) + timedelta(days=1)
        )
    if genders and len(genders) < 2:
        gender_vals = [1 if g.lower() == "male" else 0 for g in genders]
        query = query.filter(Prediction.sex.in_(gender_vals))
    if diseases and len(diseases) < 2:
        disease_vals = [1 if d.lower() == "yes" else 0 for d in diseases]
        query = query.filter(Prediction.prediction.in_(disease_vals))
    if where_clause:
        from sqlalchemy import text

        try:
            query = query.filter(text(where_clause))
        except Exception:
            pass
    rows_all = query.all()
    filtered_rows = []
    for r in rows_all:
        rpct = (r.confidence if r.prediction == 1 else 1 - r.confidence) * 100
        if min_pct <= rpct <= max_pct:
            filtered_rows.append((r, rpct))
    if sort_by == "risk_pct":
        filtered_rows.sort(key=lambda x: x[1], reverse=True)
    elif sort_by == "age":
        filtered_rows.sort(key=lambda x: x[0].age)
    else:
        filtered_rows.sort(key=lambda x: x[0].id)
    rows = [r for r, _ in filtered_rows]

    buf = io.BytesIO()
    pagesize = landscape(A4)

    doc = SimpleDocTemplate(buf, pagesize=pagesize)
    # leave a margin so images never exceed the frame and trigger LayoutError
    max_chart_w = doc.width - cm
    max_chart_h = doc.height - cm

    def fit_image(buffer: io.BytesIO, max_w: float = max_chart_w, max_h: float = max_chart_h) -> Image:
        img = Image(buffer)
        iw, ih = img.imageWidth, img.imageHeight
        scale = min(max_w / iw, max_h / ih, 1)
        img.drawWidth = iw * scale
        img.drawHeight = ih * scale
        img.hAlign = "CENTER"
        return img

    # summary statistics
    total = len(rows)
    pos = sum(r.prediction == 1 for r in rows)
    pos_rate = (pos / total * 100) if total else 0
    avg_risk = (
        sum((r.confidence if r.prediction == 1 else 1 - r.confidence) for r in rows)
        / total * 100
        if total
        else 0
    )

    # build dataframe for plots
    df = pd.DataFrame(
        [
            {
                "id": r.id,
                "age": r.age,
                "sex": SEX_MAP.get(r.sex, r.sex),
                "chest_pain": r.chest_pain_type,
                "rest_bp": r.resting_bp,
                "chol": r.cholesterol,
                "max_hr": r.max_heart_rate,
                "prediction": "Yes" if r.prediction else "No",
                "risk_pct": (r.confidence if r.prediction == 1 else 1 - r.confidence) * 100,
                "cluster_id": r.cluster_id,
                "st_depression": r.oldpeak,
            }
            for r in rows
        ]
    )

    # confusion matrix
    confmat_img = None
    if plt is not None and sns is not None and not df.empty:
        y_pred = df["prediction"].map({"Yes": 1, "No": 0}) if df["prediction"].dtype == object else df["prediction"]
        y_true = df.get("actual")
        if y_true is None:
            y_true = y_pred
        conf_mat = confusion_matrix(y_true, y_pred, labels=[0, 1])
        fig, ax = plt.subplots(figsize=(4, 4))
        sns.heatmap(
            conf_mat,
            annot=True,
            fmt="d",
            cmap="Blues",
            cbar=False,
            xticklabels=["Pred 0", "Pred 1"],
            yticklabels=["Actual 0", "Actual 1"],
            ax=ax,
        )
        ax.set_title("Confusion Matrix", fontweight="bold")
        buf_cm = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf_cm, format="PNG", dpi=150)
        plt.close(fig)
        buf_cm.seek(0)
        confmat_img = fit_image(buf_cm)

    # cluster analysis visuals
    cluster_dist_img = None
    cluster_table = None
    if plt is not None and not df.empty and df["cluster_id"].notna().any():
        cluster_df = df.dropna(subset=["cluster_id"])
        profiles = (
            cluster_df
            .groupby("cluster_id")[
                ["age", "rest_bp", "chol", "max_hr", "st_depression", "risk_pct"]
            ]
            .mean()
            .round(1)
        )
        # color mapping consistent with dashboard
        def compute_cluster_colors(info):
            if not info:
                return {}
            base = ["#f97316", "#3b82f6", "#9333ea", "#eab308"]
            sorted_info = sorted(info, key=lambda c: c["avg_risk_pct"])
            colors_map = {}
            for i, c in enumerate(sorted_info):
                cid = int(c["cluster_id"])
                if i == 0:
                    colors_map[cid] = "#22c55e"
                elif i == len(sorted_info) - 1:
                    colors_map[cid] = "#dc2626"
                else:
                    colors_map[cid] = base[(i - 1) % len(base)]
            return colors_map

        info = [
            {"cluster_id": int(cid), "avg_risk_pct": row["risk_pct"]}
            for cid, row in profiles.iterrows()
        ]
        cluster_colors = compute_cluster_colors(info)

        # cluster risk distribution KDE
        xs = np.arange(0, 101, 1)
        fig, ax = plt.subplots(figsize=(6, 4))
        for cid, sub in cluster_df.groupby("cluster_id"):
            vals = sub["risk_pct"].dropna().to_numpy()
            if len(vals) == 0:
                continue
            sample = vals
            if len(sample) > 2000:
                step = math.ceil(len(sample) / 2000)
                sample = sample[::step]
            n = len(sample)
            mean = sample.mean()
            variance = ((sample - mean) ** 2).sum() / n
            sd = math.sqrt(variance) or 1
            bw = 1.06 * sd * (n ** (-1 / 5))
            ys = []
            for x in xs:
                u = (x - sample) / bw
                ys.append(np.exp(-0.5 * u * u).sum() / (n * bw * math.sqrt(2 * math.pi)))
            color = cluster_colors.get(int(cid), "#888888")
            ax.plot(xs, ys, color=color, linewidth=2, label=f"Cluster {int(cid)}")
            ax.fill_between(xs, ys, color=color, alpha=0.2)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Risk %")
        ax.set_ylabel("Density")
        ax.set_title("Cluster Risk Distribution", fontweight="bold")
        ax.legend()
        ax.set_aspect("auto")
        buf_kde = io.BytesIO()
        fig.tight_layout()
        fig.savefig(buf_kde, format="PNG", dpi=150, bbox_inches="tight")
        plt.close(fig)
        buf_kde.seek(0)
        cluster_dist_img = fit_image(buf_kde)

        # cluster profile table
        cluster_table_data = [
            ["Cluster", "Avg Age", "Avg Rest BP", "Avg Chol", "Avg Max HR", "Avg ST Dep"]
        ]
        for cid, row in profiles.iterrows():
            cluster_table_data.append(
                [
                    int(cid),
                    row["age"],
                    row["rest_bp"],
                    row["chol"],
                    row["max_hr"],
                    row["st_depression"],
                ]
            )
        cluster_table = Table(
            cluster_table_data,
            repeatRows=1,
            colWidths=[doc.width / len(cluster_table_data[0])] * len(cluster_table_data[0]),
        )
        cluster_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lavender]),
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                ]
            )
        )

    styles = getSampleStyleSheet()
    gen_date = datetime.now(ZoneInfo("Asia/Colombo")).strftime("%Y-%m-%d %H:%M IST")
    logo_path = os.path.join(app.root_path, "static", "logo.svg")

    def header_footer(c, doc):
        width, height = doc.pagesize
        c.saveState()
        bg = colors.black if theme == "dark" else colors.white
        text_col = colors.white if theme == "dark" else colors.black
        c.setFillColor(bg)
        c.rect(0, 0, width, height, stroke=0, fill=1)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.HexColor("#dc2626"))
        c.drawString(cm, height - cm + 4, "\u2665")
        c.setFillColor(text_col)
        c.drawString(cm + 14, height - cm, "Heart Disease Risk App")
        try:
            c.drawImage(
                logo_path,
                width - 3 * cm,
                height - 1.5 * cm,
                width=2 * cm,
                preserveAspectRatio=True,
                mask="auto",
            )
        except Exception:
            pass

        c.setFont("Helvetica", 9)
        c.drawString(cm, cm / 2, f"Generated {gen_date}")
        page = c.getPageNumber()
        c.drawRightString(width - cm, cm / 2, f"Page {page}")
        c.restoreState()

    # records table with dynamic column widths
    col_map = {
        "id": ("ID", lambda r: r.id),
        "age": ("Age", lambda r: r.age),
        "sex": ("Sex", lambda r: SEX_MAP.get(r.sex, r.sex)),
        "chest_pain": ("Chest pain", lambda r: r.chest_pain_type),
        "rest_bp": ("Rest BP", lambda r: r.resting_bp),
        "cholesterol": ("Chol", lambda r: r.cholesterol),
        "max_hr": ("Max HR", lambda r: r.max_heart_rate),
        "pred_label": ("Pred", lambda r: "Yes" if r.prediction else "No"),
        "risk_pct": (
            "Risk %",
            lambda r: f"{round((r.confidence if r.prediction == 1 else 1 - r.confidence) * 100, 1)}%",
        ),
    }
    headers = [col_map[c][0] for c in columns]
    table_data = [headers]
    for r in rows:
        table_data.append([col_map[c][1](r) for c in columns])
    max_lengths = [max(len(str(row[i])) for row in table_data) for i in range(len(headers))]
    total_len = sum(max_lengths)
    col_fracs = []
    for h, L in zip(headers, max_lengths):
        frac = L / total_len if total_len else 1 / len(headers)
        if h == "Chest pain":
            frac = max(frac, 0.15)
        elif h in {"ID", "Age", "Sex", "Pred", "Risk %"}:
            frac = max(frac, 0.05)
        col_fracs.append(frac)
    frac_sum = sum(col_fracs)
    col_widths = [doc.width * (f / frac_sum) for f in col_fracs]

    table = Table(table_data, repeatRows=1, colWidths=col_widths)
    table_styles = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.lavender]),
        ("ALIGN", (0, 1), (-1, -1), "CENTER"),
        ("ALIGN", (3, 1), (3, -1), "LEFT"),
    ]
    id_idx = columns.index("id") if "id" in columns else None
    for row_idx, r in enumerate(rows, start=1):
        pred_val = "Yes" if r.prediction else "No"
        if id_idx is not None and "pred_label" in columns and pred_val == "Yes":
            table_styles.extend(
                [
                    ("TEXTCOLOR", (id_idx, row_idx), (id_idx, row_idx), colors.HexColor("#b22222")),
                    ("FONTNAME", (id_idx, row_idx), (id_idx, row_idx), "Helvetica-Bold"),
                ]
            )
    table.setStyle(TableStyle(table_styles))

    toc_items = []
    if include_results:
        toc_items.append("Summary stats")
    if include_visuals:
        toc_items.append("Visualizations")
    if notes:
        toc_items.append("Doctor's notes")
    if include_patient or include_inputs:
        toc_items.append("Records")

    elements: list = []
    if len(toc_items) > 1:
        elements.append(Paragraph("<b>Table of Contents</b>", styles["Title"]))
        elements.append(Spacer(1, 0.5 * cm))
        for i, item in enumerate(toc_items, start=1):
            elements.append(Paragraph(f"{i}. {item}", styles["Normal"]))
        elements.append(PageBreak())

    if include_results:
        elements.extend(
            [
                Paragraph("<b>Predictions Summary</b>", styles["Title"]),
                Spacer(1, 0.5 * cm),
                Paragraph(f"Total predictions: {total}", styles["Normal"]),
                Paragraph(f"Positive rate: {pos_rate:.1f}%", styles["Normal"]),
                Paragraph(
                    f"Average risk probability: {avg_risk:.1f}%",
                    styles["Normal"],
                ),
            ]
        )
        if include_visuals or notes or include_patient or include_inputs:

            elements.append(PageBreak())

    if include_visuals:
        elements.extend([
            Paragraph("<b>Visualizations</b>", styles["Title"]),
            Spacer(1, 0.5 * cm),
        ])
        if confmat_img is not None:
            elements.append(confmat_img)
            elements.append(Spacer(1, 0.5 * cm))
        if cluster_dist_img is not None:
            elements.append(cluster_dist_img)
            elements.append(Spacer(1, 0.5 * cm))
        if cluster_table is not None:
            elements.append(cluster_table)
            elements.append(Spacer(1, 0.5 * cm))
        if notes or include_patient or include_inputs:
            elements.append(PageBreak())

    if notes:
        elements.append(Paragraph("<b>Doctor's notes</b>", styles["Title"]))
        elements.append(Paragraph(notes.replace("\n", "<br/>"), styles["Normal"]))
        elements.append(Spacer(1, 0.5 * cm))

    if include_patient or include_inputs:
        elements.append(Paragraph("<b>Records</b>", styles["Title"]))
        elements.append(table)

    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name="predictions.pdf",
        mimetype="application/pdf",
    )



@app.get("/dashboard/csv")
@login_required
def dashboard_csv():
    import csv

    rows = Prediction.query.order_by(Prediction.created_at.asc()).all()
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["ID", "Age", "Sex", "Chest pain", "Rest BP", "Chol", "Max HR", "Pred", "Risk %"])
    for r in rows:
        risk = r.confidence if r.prediction == 1 else (1 - r.confidence)
        writer.writerow([
            r.id,
            r.age,
            SEX_MAP.get(r.sex, r.sex),
            r.chest_pain_type,
            r.resting_bp,
            r.cholesterol,
            r.max_heart_rate,
            'Yes' if r.prediction else 'No',
            f"{round(risk * 100, 1)}%"
        ])
    data = buf.getvalue().encode('utf-8')
    return send_file(
        io.BytesIO(data),
        as_attachment=True,
        download_name="predictions.csv",
        mimetype="text/csv",
    )


@app.get("/dashboard/clean-csv")
@login_required
def dashboard_clean_csv():
    rows = Prediction.query.order_by(Prediction.created_at.asc()).all()
    data = [r.to_dict() for r in rows]
    if data:
        df = pd.DataFrame(data)
        clean_df, _ = combine_outlier_reports(df)
        csv_text = clean_df.drop(columns=["patient_name"], errors="ignore").to_csv(index=False)
    else:
        csv_text = ""
    return send_file(
        io.BytesIO(csv_text.encode("utf-8")),
        as_attachment=True,
        download_name="predictions_clean.csv",
        mimetype="text/csv",
    )


@app.get("/research")
@login_required
def research_paper():
    paper = load_research_paper()
    return render_template("research/index.html", paper=paper)

# ---------------------------
# PDF single report
# ---------------------------
@app.get("/report/<int:pid>")
@login_required
def report(pid: int):
    pred = Prediction.query.get_or_404(pid)
    buf = generate_prediction_pdf(pred, SEX_MAP, YESNO)
    return send_file(buf, as_attachment=True, download_name=f"report_{pred.id}.pdf", mimetype="application/pdf")

# ============================
# CSV Upload / Cleaning / EDA / Batch Predict
# ============================

def _safe_read_csv(fobj) -> pd.DataFrame:
    try:
        return pd.read_csv(fobj)
    except UnicodeDecodeError:
        fobj.seek(0)
        return pd.read_csv(fobj, encoding="latin-1")

# ---------- EDA helpers ----------

def _winsorize_series(s: pd.Series, lower=0.01, upper=0.99):
    s_num = pd.to_numeric(s, errors="coerce")
    ql, qu = s_num.quantile([lower, upper])
    clipped = s_num.clip(ql, qu)
    n_changed = int((~clipped.eq(s_num)).sum())
    return clipped, n_changed, float(ql), float(qu)


def _strip_count_from_stats(stats: dict) -> dict:
    if not isinstance(stats, dict):
        return stats
    for k, v in list(stats.items()):
        if isinstance(v, dict):
            v.pop("count", None)
    stats.pop("count", None)
    return stats

def _shared_hist(series_by_group: dict[str, pd.Series], nbins: int = 20):
    """Compute shared-bin histograms for multiple groups.
    Returns: {"bins": centers, "series": [{"name":..., "counts":[...]}, ...]}
    """
    all_values = pd.concat([s.dropna() for s in series_by_group.values()]) if series_by_group else pd.Series([], dtype=float)
    if all_values.empty:
        return {"bins": [], "series": []}
    counts, edges = np.histogram(all_values, bins=nbins)
    centers = ((edges[:-1] + edges[1:]) / 2).tolist()
    out_series = []
    for name, s in series_by_group.items():
        vals = s.dropna().values
        if len(vals) == 0:
            out_series.append({"name": name, "counts": [0]*len(centers)})
        else:
            c, _ = np.histogram(vals, bins=edges)
            out_series.append({"name": name, "counts": c.astype(int).tolist()})
    return {"bins": centers, "series": out_series}


def build_eda_payload(df: pd.DataFrame) -> dict:
    # Positive probability distribution (if available)
    prob_dist = None
    if "positive_probability" in df.columns:
        vals = pd.to_numeric(df["positive_probability"], errors="coerce").dropna().values
        if vals.size:
            counts, edges = np.histogram(vals, bins=20, range=(0, 1))
            centers = (edges[:-1] + edges[1:]) / 2

            # Normal fit for a “bell-curve” overlay, scaled to histogram area
            n = vals.size
            mu = float(vals.mean())
            sigma = float(vals.std(ddof=1)) if n > 1 else 0.0
            bin_width = float(edges[1] - edges[0])
            if sigma > 0:
                normal_y = (1.0 / (sigma * np.sqrt(2*np.pi))) * np.exp(-0.5 * ((centers - mu)/sigma)**2)
                normal_y = (normal_y * n * bin_width).tolist()
            else:
                normal_y = [0.0] * len(centers)

            prob_dist = {
                "x": centers.tolist(),
                "y": counts.astype(int).tolist(),
                "normal_fit": {"mu": mu, "sigma": sigma, "y": normal_y}
            }
        else:
            prob_dist = {"x": [], "y": [], "normal_fit": {"mu": None, "sigma": None, "y": []}}







    # # After you compute centers and counts for positive_probability
    # n = int(vals.size)
    # mu = float(vals.mean())
    # sigma = float(vals.std(ddof=1)) if n > 1 else 0.0
    # bin_width = float(edges[1] - edges[0])
    # if sigma > 0:
    #     # Normal PDF scaled to histogram scale
    #     normal_y = (1.0 / (sigma * np.sqrt(2*np.pi))) * np.exp(-0.5 * ((np.array(centers) - mu)/sigma)**2)
    #     normal_y = (normal_y * n * bin_width).tolist()
    # else:
    #     normal_y = [0.0] * len(centers)

    # prob_dist = {
    #     "x": centers,
    #     "y": counts.astype(int).tolist(),
    #     "normal_fit": {"mu": mu, "sigma": sigma, "y": normal_y}
    # }


    # optional: p-values via scipy if installed
    try:
        from scipy.stats import chi2_contingency  # type: ignore
        _HAS_SCIPY = True
    except Exception:
        _HAS_SCIPY = False

    # ----- numeric summary (drop 'count') -----
    num_cols = list((NUMERIC_FEATURES_INT | NUMERIC_FEATURES_FLOAT))
    present_num = [c for c in num_cols if c in df.columns]
    if present_num:
        desc = df[present_num].describe().round(2)
        if "count" in desc.index:
            desc = desc.drop(index="count")
        stats = desc.to_dict()
    else:
        stats = {}

    # ----- histograms for numerics -----
    hists = {}
    for c in present_num:
        vals = df[c].dropna().values
        if len(vals):
            counts, edges = np.histogram(vals, bins=20)
            centers = (edges[:-1] + edges[1:]) / 2
            hists[c] = {"x": centers.tolist(), "y": counts.tolist()}
        else:
            hists[c] = {"x": [], "y": []}

    # ----- numeric correlation -----
    corr = df[present_num].corr(numeric_only=True).fillna(0) if present_num else pd.DataFrame()
    corr_payload = {
        "z": (corr.values.tolist() if not corr.empty else []),
        "x": (list(corr.columns) if not corr.empty else []),
        "y": (list(corr.index) if not corr.empty else [])
    }

    # ----- choose a target-like column if available -----
    # Many heart-disease datasets use different column names for the
    # ground-truth label (e.g. ``HeartDisease``).  Normalize lookups so
    # EDA visualisations that require a target column (such as "Resting
    # Blood Pressure by Status") still render even when the uploaded CSV
    # uses a different heading.
    target_col = None
    lower_map = {c.lower(): c for c in df.columns}
    if "num" in lower_map:             # staged 0..4 (if present)
        target_col = lower_map["num"]
    elif "target" in lower_map:        # 0/1
        target_col = lower_map["target"]
    elif "prediction" in lower_map:    # 0/1 after batch predict
        target_col = lower_map["prediction"]
    elif "heartdisease" in lower_map:  # e.g. HeartDisease (Yes/No)
        target_col = lower_map["heartdisease"]
    elif "heart_disease" in lower_map:  # alternative snake_case name
        target_col = lower_map["heart_disease"]

    # ----- categorical columns present -----
    cat_cols = [c for c in CATEGORICAL_FEATURES if c in df.columns]

    # ----- categorical distributions -----
    categorical = {}
    for col in cat_cols:
        vc = df[col].astype(str).value_counts(dropna=False)
        labels = [str(x) for x in vc.index.tolist()]
        counts = vc.values.astype(int).tolist()
        total = int(vc.sum()) if int(vc.sum()) else 1
        percents = [round(100.0 * v / total, 2) for v in vc.values.tolist()]
        categorical[col] = {
            "counts": {"labels": labels, "counts": counts, "percents": percents}
        }

    # ----- categorical vs target (stacked %) -----
    cat_vs_target = {}
    if target_col is not None:
        y = df[target_col].astype(str)
        for col in cat_cols:
            ct = pd.crosstab(df[col].astype(str), y, dropna=False).fillna(0)
            with np.errstate(divide="ignore", invalid="ignore"):
                row_pct = (ct.div(ct.sum(axis=1).replace(0, np.nan), axis=0) * 100).fillna(0)
            cat_vs_target[col] = {
                "index": ct.index.tolist(),
                "columns": ct.columns.tolist(),
                "counts": ct.values.astype(int).tolist(),
                "col_percents": row_pct.values.round(2).tolist()
            }

    # ----- Cramér’s V helpers -----
    def _cramers_v(table: pd.DataFrame) -> float:
        n = table.values.sum()
        if n == 0:
            return 0.0
        row_sums = table.sum(axis=1).values.reshape(-1, 1)
        col_sums = table.sum(axis=0).values.reshape(1, -1)
        expected = row_sums.dot(col_sums) / n
        with np.errstate(divide="ignore", invalid="ignore"):
            chi2 = np.nansum((table.values - expected) ** 2 / np.where(expected == 0, np.nan, expected))
        k = table.shape[1]
        r = table.shape[0]
        denom = n * (min(k - 1, r - 1))
        if denom <= 0:
            return 0.0
        v = math.sqrt(max(chi2, 0.0) / denom)
        return float(v)

    # ----- categorical associations vs target -----
    cat_associations = []
    if target_col is not None:
        y = df[target_col].astype(str)
        for col in cat_cols:
            ct = pd.crosstab(df[col].astype(str), y, dropna=False)
            v = _cramers_v(ct)
            pval = None
            if _HAS_SCIPY:
                try:
                    _, p, _, _ = chi2_contingency(ct.values, correction=False)
                    pval = float(p)
                except Exception:
                    pval = None
            cat_associations.append({
                "col": col,
                "cramers_v": round(v, 4),
                "p_value": (None if pval is None else round(pval, 6))
            })

    # ----- categorical association matrix (Cramér’s V between cats) -----
    cat_assoc_matrix = None
    if len(cat_cols) >= 2:
        z = []
        for rcol in cat_cols:
            row_vals = []
            for ccol in cat_cols:
                ct = pd.crosstab(df[rcol].astype(str), df[ccol].astype(str), dropna=False)
                row_vals.append(round(_cramers_v(ct), 4))
            z.append(row_vals)
        cat_assoc_matrix = {"z": z, "x": cat_cols, "y": cat_cols}

    # ----- optional raw target distribution -----
    target_dist = None
    if target_col is not None:
        counts = df[target_col].astype(str).value_counts(dropna=False).to_dict()
        target_dist = {"labels": list(counts.keys()), "values": list(counts.values())}

    # ==========================================================
    # Enhanced Plotly-ready visual payloads for the frontend
    # ==========================================================



    # ==========================================================
    # NEW: Notebook-style visual payloads for Plotly in frontend
    # ==========================================================
    # Map for sex labels (0/1 -> Female/Male) when we want readable axes
    def _sex_label(val):
        try:
            ival = int(val)
            return SEX_MAP.get(ival, str(val))
        except Exception:
            return str(val)

    # 1) Gender distribution (Pie)
    gender_pie = None
    if "sex" in df.columns:
        vc = df["sex"].value_counts(dropna=False)
        labels = [ _sex_label(x) for x in vc.index.tolist() ]
        values = vc.values.astype(int).tolist()
        gender_pie = {"labels": labels, "values": values}  # Plotly: go.Pie(labels, values, ...)

    # 2) Heatmap: Dataset × Gender Counts
    # We treat "dataset" as your notebook’s name; in this app it’s "country" if present.
    ds_col = "dataset" if "dataset" in df.columns else ("country" if "country" in df.columns else None)
    dataset_gender_heatmap = None
    if ds_col is not None and "sex" in df.columns:
        tmp = df[[ds_col, "sex"]].dropna()
        if not tmp.empty:
            counts = tmp.groupby([ds_col, "sex"]).size().reset_index(name="Count")
            pivot = counts.pivot(index=ds_col, columns="sex", values="Count").fillna(0)
            x = [_sex_label(c) for c in pivot.columns.tolist()]
            y = pivot.index.astype(str).tolist()
            z = pivot.values.astype(int).tolist()
            dataset_gender_heatmap = {"x": x, "y": y, "z": z}  # Plotly: go.Heatmap(z, x, y, ...)

    # 3) Age distribution per dataset (shared-bin overlay hist) + box by dataset
    age_hist_by_dataset = None
    age_box_by_dataset = None
    if "age" in df.columns and ds_col is not None and df[ds_col].notna().any():
        groups = {str(name): grp["age"] for name, grp in df.groupby(ds_col)}
        age_hist_by_dataset = _shared_hist(groups, nbins=20)
        age_box_by_dataset = [
            {"name": name, "values": series.dropna().tolist()}
            for name, series in groups.items()
        ]



    # 4) Age distribution by Chest Pain Type (facet-like data)
    age_by_cp = None
    cp_col = "chest_pain_type" if "chest_pain_type" in df.columns else ("cp" if "cp" in df.columns else None)
    if "age" in df.columns and cp_col is not None:
        by_cp = {}
        for cpv, sub in df.groupby(cp_col):
            by_cp[str(cpv)] = sub["age"].dropna().tolist()
        age_by_cp = by_cp  # Frontend can build px-like facets

    # 5) Resting Blood Pressure boxplots by heart disease status
    bp_box_by_status = None
    if "resting_blood_pressure" in df.columns:
        series = [
            {
                "name": "All Patients",
                "values": df["resting_blood_pressure"].dropna().tolist(),
            }
        ]
        status_col = target_col  # prefer staged num if present, else 0/1 target/prediction
        if status_col is not None:
            uniq = sorted(df[status_col].dropna().unique().tolist())
            try:
                uniq_num = set(int(float(x)) for x in uniq)
            except Exception:
                uniq_num = None
            if uniq_num and uniq_num.issubset({0, 1}):
                series.append(
                    {
                        "name": "No Disease",
                        "values": df[
                            df[status_col]
                            .astype(float)
                            .fillna(-1)
                            .astype(int)
                            == 0
                        ]["resting_blood_pressure"].dropna().tolist(),
                    }
                )
                series.append(
                    {
                        "name": "Heart Disease",
                        "values": df[
                            df[status_col]
                            .astype(float)
                            .fillna(-1)
                            .astype(int)
                            == 1
                        ]["resting_blood_pressure"].dropna().tolist(),
                    }
                )
            else:
                for st in uniq:
                    series.append(
                        {
                            "name": str(st),
                            "values": df[df[status_col] == st][
                                "resting_blood_pressure"
                            ]
                            .dropna()
                            .tolist(),
                        }
                    )
        bp_box_by_status = series

    # 6) Resting BP histogram stacked by stage (or by target)
    bp_hist_by_stage = None
    if "resting_blood_pressure" in df.columns and target_col is not None:
        groups = {}
        uniq = sorted(df[target_col].dropna().unique().tolist())
        try:
            uniq_num = set(int(float(x)) for x in uniq)
        except Exception:
            uniq_num = None
        if uniq_num and uniq_num.issubset({0, 1}):
            groups["0 - No Disease"] = df[
                df[target_col].astype(float).fillna(-1).astype(int) == 0
            ]["resting_blood_pressure"]
            groups["1 - Heart Disease"] = df[
                df[target_col].astype(float).fillna(-1).astype(int) == 1
            ]["resting_blood_pressure"]
        else:
            for st in uniq:
                groups[str(st)] = df[df[target_col] == st][
                    "resting_blood_pressure"
                ]
        bp_hist_by_stage = _shared_hist(groups, nbins=20)

    # 7) Cholesterol violin by stage (or target)
    chol_violin_by_stage = None
    if "cholesterol" in df.columns:
        series = [
            {
                "name": "All Patients",
                "values": df["cholesterol"].dropna().tolist(),
            }
        ]
        if target_col is not None:
            uniq = sorted(df[target_col].dropna().unique().tolist())
            try:
                uniq_num = set(int(float(x)) for x in uniq)
            except Exception:
                uniq_num = None
            if uniq_num and uniq_num.issubset({0, 1}):
                series.append(
                    {
                        "name": "No Disease",
                        "values": df[
                            df[target_col]
                            .astype(float)
                            .fillna(-1)
                            .astype(int)
                            == 0
                        ]["cholesterol"].dropna().tolist(),
                    }
                )
                series.append(
                    {
                        "name": "Heart Disease",
                        "values": df[
                            df[target_col]
                            .astype(float)
                            .fillna(-1)
                            .astype(int)
                            == 1
                        ]["cholesterol"].dropna().tolist(),
                    }
                )
            else:
                for st in uniq:
                    series.append(
                        {
                            "name": str(st),
                            "values": df[df[target_col] == st]["cholesterol"].dropna().tolist(),
                        }
                    )
        chol_violin_by_stage = series

    viz_payload = {
        "gender_pie": gender_pie,                              # -> go.Pie(labels, values, ...)
        "dataset_gender_heatmap": dataset_gender_heatmap,      # -> go.Heatmap(z, x, y, ...)
        "age_hist_by_dataset": age_hist_by_dataset,            # -> overlay hist (bins + per-dataset counts)
        "age_box_by_dataset": age_box_by_dataset,              # -> list of {name, values}
        "age_by_cp": age_by_cp,                                # -> dict cp -> list of ages
        "bp_box_by_status": bp_box_by_status,                  # -> list of {name, values}
        "bp_hist_by_stage": bp_hist_by_stage,                  # -> stacked hist (bins + per-stage counts)
        "chol_violin_by_stage": chol_violin_by_stage           # -> list of {name, values}
    }

    return {
        "stats": stats,
        "hists": hists,
        "corr": corr_payload,
        "target": target_dist,
        "categorical": categorical,
        "cat_vs_target": cat_vs_target,
        "cat_associations": cat_associations,
        "cat_assoc_matrix": cat_assoc_matrix,
        "viz": viz_payload,
        "probability_distribution": prob_dist
    }











# ============================
# Upload session helpers
# ============================
def _make_upload_dir() -> tuple[str, str]:
    uid = uuid.uuid4().hex[:12]
    path = os.path.join(UPLOADS_DIR, uid)
    os.makedirs(path, exist_ok=True)
    return uid, path

def _paths(uid: str) -> dict:
    base = os.path.join(UPLOADS_DIR, uid)
    return {
        "base": base,
        "raw": os.path.join(base, "raw.csv"),
        "mapped": os.path.join(base, "mapped.csv"),
        "clean": os.path.join(base, "clean.csv"),
        "results": os.path.join(base, "results.csv"),
        "eda_json": os.path.join(base, "eda.json"),
        "pre_log": os.path.join(base, "pre_log.json"),
    }

# ========= Column mapping helpers =========
def _best_guess_mapping(upload_cols: list[str]) -> dict:
    rev = {k: v for k, v in COLUMN_ALIASES.items()}
    def norm(h): return str(h).strip().lower().replace(" ", "_")
    uploaded_to_internal = {}
    for c in upload_cols:
        n = norm(c)
        uploaded_to_internal[c] = rev.get(n, None)
    chosen = {col: "" for col in INPUT_COLUMNS}
    used = set()
    # pass 1: exact alias hits
    for up, internal in uploaded_to_internal.items():
        if internal and internal in chosen and not chosen[internal]:
            chosen[internal] = up
            used.add(up)
    # pass 2: loose substring guesses
    for need in INPUT_COLUMNS:
        if not chosen[need]:
            nneed = norm(need)
            for up in upload_cols:
                if up in used:
                    continue
                if nneed in norm(up) or norm(up) in nneed:
                    chosen[need] = up
                    used.add(up)
                    break
    return chosen

def _save_map_payload(uid: str, upload_cols: list[str], proposal: dict):
    p = _paths(uid)
    payload = {"uploaded_columns": upload_cols, "proposal": proposal}
    with open(os.path.join(p["base"], "map.json"), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

def _load_map_payload(uid: str) -> dict | None:
    p = _paths(uid)
    fpath = os.path.join(p["base"], "map.json")
    if not os.path.exists(fpath):
        return None
    with open(fpath, "r", encoding="utf-8") as f:
        return json.load(f)

def _apply_user_mapping(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    picked = {}
    for internal_col, uploaded_col in mapping.items():
        if not uploaded_col or uploaded_col not in df.columns:
            if internal_col in OPTIONAL_KEEP:
                continue
            raise ValueError(f"Missing mapping for '{internal_col}'")
        picked[internal_col] = df[uploaded_col]

    # always include model-required columns
    new_df = pd.DataFrame({col: picked[col] for col in INPUT_COLUMNS})

    # --- add optional keep if present ---
    # 1) if user explicitly mapped it (in case you add it to the UI later)
    for col in OPTIONAL_KEEP:
        if col in picked:
            new_df[col] = picked[col]
    # 2) otherwise, auto-detect in the raw CSV via aliases (so 'dataset' or 'country' works)
    if "country" not in new_df.columns:
        raw_country = find_optional_in_raw(df, "country")
        if raw_country:
            new_df["country"] = df[raw_country]

    return new_df


# ============================
# CSV/EDA Routes
# ============================
@app.get("/upload")
@login_required
def upload_form():
    return render_template("uploads/form.html",
                           required_cols=sorted(list(REQUIRED_INTERNAL_COLUMNS)),
                           model_name=model_name)

@app.post("/upload")
@login_required
@csrf_protect
def upload_post():
    file = request.files.get("file")
    if not file or file.filename == "":
        if request.args.get("ajax") == "1":
            return jsonify({"error": "No file selected"}), 400
        return render_template("error.html", title="No file selected",
                               messages=["Please choose a .csv file to upload."]), 400

    fname = secure_filename(file.filename)
    if not fname.lower().endswith(".csv"):
        if request.args.get("ajax") == "1":
            return jsonify({"error": "Only .csv files are supported."}), 400
        return render_template("error.html", title="Invalid file type",
                               messages=["Only .csv files are supported."]), 400

    uid, _dir = _make_upload_dir()
    p = _paths(uid)
    file.save(p["raw"])

    try:
        with open(p["raw"], "rb") as f:
            df_raw = _safe_read_csv(f)
    except Exception as e:
        if request.args.get("ajax") == "1":
            return jsonify({"error": f"{type(e).__name__}: {e}"}), 400
        return render_template("error.html", title="Failed to read CSV",
                               messages=[f"{type(e).__name__}: {e}"]), 400

    log: list[str] = []
    df_norm = normalize_columns(df_raw, log)
    ok, errs = validate_structure(df_norm)
    if ok:
        df_norm.to_csv(p["mapped"], index=False)
        with open(p["pre_log"], "w", encoding="utf-8") as f:
            json.dump({"log": log, "orig_rows": len(df_norm)}, f)
        next_url = url_for("upload_preprocess", uid=uid)
        if request.args.get("ajax") == "1":
            return jsonify({"redirect": next_url})
        return redirect(next_url)
    else:
        upload_cols = list(df_raw.columns)
        proposal = _best_guess_mapping(upload_cols)
        _save_map_payload(uid, upload_cols, proposal)
        next_url = url_for("upload_columns_map", uid=uid)
        if request.args.get("ajax") == "1":
            return jsonify({"redirect": next_url})
        return redirect(next_url)

@app.get("/upload/<uid>/columns")
@login_required
def upload_columns_map(uid: str):
    p = _paths(uid)
    if not os.path.exists(p["raw"]):
        return render_template("error.html", title="Session expired",
                               messages=["We couldn't find your uploaded file. Please upload again."]), 404

    payload = _load_map_payload(uid)
    if not payload:
        with open(p["raw"], "rb") as f:
            df = _safe_read_csv(f)
        upload_cols = list(df.columns)
        proposal = _best_guess_mapping(upload_cols)
        _save_map_payload(uid, upload_cols, proposal)
        payload = _load_map_payload(uid)

    mapping_tips = {
        "age": "Tip: map age here.",
        "sex": "Tip: map sex here.",
        "chest_pain_type": "Tip: map cp here (typical, atypical, non-anginal, asymptomatic).",
        "resting_blood_pressure": "Tip: map trestbps here.",
        "cholesterol": "Tip: map chol here.",
        "fasting_blood_sugar": "Tip: map fbs here (TRUE/FALSE or 1/0).",
        "Restecg": "Tip: map restecg here.",
        "max_heart_rate_achieved": "Tip: map thalch or thalach here.",
        "exercise_induced_angina": "Tip: map exang here.",
        "st_depression": "Tip: map oldpeak here.",
        "st_slope_type": "Tip: map slope here.",
        "num_major_vessels": "Tip: map ca here (0–4).",
        "thalassemia_type": "Tip: map thal here (normal, fixed defect, reversible defect).",
    }
    var_info = [
        {"var": "age", "type": "Integer", "desc": "Age of patient (years)"},
        {"var": "sex", "type": "Categorical", "desc": "Gender"},
        {"var": "cp", "type": "Categorical", "desc": "Chest pain type"},
        {"var": "trestbps", "type": "Integer", "desc": "Resting blood pressure (mm Hg)"},
        {"var": "chol", "type": "Integer", "desc": "Serum cholesterol (mg/dL)"},
        {"var": "fbs", "type": "Categorical", "desc": "Fasting blood sugar >120 mg/dL"},
        {"var": "restecg", "type": "Categorical", "desc": "Resting ECG results"},
        {"var": "thalach", "type": "Integer", "desc": "Maximum heart rate achieved"},
        {"var": "exang", "type": "Categorical", "desc": "Exercise-induced angina"},
        {"var": "oldpeak", "type": "Float", "desc": "ST depression induced by exercise relative to rest"},
        {"var": "slope", "type": "Categorical", "desc": "Slope of peak exercise ST segment"},
        {"var": "ca", "type": "Integer", "desc": "Major vessels colored by fluoroscopy (0–4)"},
        {"var": "thal", "type": "Categorical", "desc": "Thalium stress test result"},
        {"var": "target", "type": "Integer", "desc": "Heart disease presence (0 = no, 1 = yes)"},
    ]

    return render_template(
        "uploads/columns_map.html",
        uid=uid,
        required_cols=INPUT_COLUMNS,
        uploaded_cols=payload["uploaded_columns"],
        proposal=payload["proposal"],
        mapping_tips=mapping_tips,
        var_info=var_info,
        model_name=model_name
    )

@app.post("/upload/<uid>/columns")
@login_required
@csrf_protect
def upload_columns_map_submit(uid: str):
    p = _paths(uid)
    if not os.path.exists(p["raw"]):
        return render_template("error.html", title="Session expired",
                               messages=["We couldn't find your uploaded file. Please upload again."]), 404

    mapping = {col: (request.form.get(f"map__{col}", "").strip()) for col in INPUT_COLUMNS}

    chosen = [v for v in mapping.values() if v]
    if len(chosen) != len(set(chosen)):
        return render_template("error.html", title="Invalid mapping",
                               messages=["Each uploaded column can be used only once. Please revise."]), 400
    missing = [k for k, v in mapping.items() if not v]
    if missing:
        return render_template("error.html", title="Missing selections",
                               messages=[f"Please select a source column for: {', '.join(missing)}"]), 400

    with open(p["raw"], "rb") as f:
        df_raw = _safe_read_csv(f)

    try:
        df_mapped = _apply_user_mapping(df_raw, mapping)
    except Exception as e:
        return render_template("error.html", title="Mapping error", messages=[str(e)]), 400
    df_mapped.to_csv(p["mapped"], index=False)
    with open(p["pre_log"], "w", encoding="utf-8") as f:
        json.dump({
            "log": [{"text": "User provided column mapping.", "step": "info"}],
            "orig_rows": len(df_mapped),
        }, f)
    return redirect(url_for("upload_preprocess", uid=uid))



@app.get("/upload/<uid>/preprocess")
@login_required
def upload_preprocess(uid: str):
    p = _paths(uid)
    if not os.path.exists(p["mapped"]):
        return render_template(
            "error.html",
            title="Session expired",
            messages=["We couldn't find your mapped dataset. Please upload again."],
        ), 404
    df = pd.read_csv(p["mapped"])
    preview = df.head(5).drop(columns=["patient_name"], errors="ignore").to_dict(orient="records")
    return render_template("uploads/preprocess.html", uid=uid, preview_json=preview)



@app.post("/upload/<uid>/preprocess/<task>")
@login_required
@csrf_protect_api
def upload_preprocess_task(uid: str, task: str):
    p = _paths(uid)
    if not os.path.exists(p["mapped"]):
        return jsonify({"ok": False, "error": "No mapped dataset"}), 404
    try:
        df = pd.read_csv(p["mapped"])
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    opts = {
        "handle_duplicates": False,
        "invalid_to_nan": False,
        "impute_missing": False,
        "soften_outliers": False,
    }
    if task == "dup":
        opts["handle_duplicates"] = True
    elif task == "invalid":
        opts["invalid_to_nan"] = True
    elif task == "impute":
        opts["impute_missing"] = True
    elif task == "outliers":
        opts["soften_outliers"] = True
    else:
        return jsonify({"ok": False, "error": "Unknown task"}), 400

    TASK_INFO = {
        "dup": "Removed exact duplicate rows using pandas drop_duplicates (kept first occurrence).",
        "invalid": "Replaced implausible values with NaN so they can be imputed later.",
        "impute": "Filled missing values via median (numeric) or Random Forest (categorical).",
        "outliers": "Clipped extreme numeric values outside 1.5×IQR range to soften outliers.",
    }

    dup_rows: list[dict] = []
    if task == "dup":
        dup_rows = df[df.duplicated()].replace({np.nan: None}).to_dict(orient="records")

    try:
        df_clean, clog = clean_dataframe(df, **opts)
    except Exception as e:
        return jsonify({"ok": False, "error": f"{type(e).__name__}: {e}"}), 400
    clog = [m for m in clog if "skipped" not in m and "0 renamed" not in m and not m.startswith("Final rows")]
    df_clean.to_csv(p["mapped"], index=False)

    # persist log with optional detail payloads

    log_path = p["pre_log"]
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"log": [], "orig_rows": len(df)}

    entries = []
    for m in clog:
        entry = {"text": m, "step": task}
        if task == "dup" and dup_rows:
            entry["details"] = dup_rows
        entries.append(entry)
    data["log"].extend(entries)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    preview = df_clean.head(5).drop(columns=["patient_name"], errors="ignore").replace({np.nan: None}).to_dict(orient="records")
    return jsonify({
        "ok": True,
        "message": "; ".join(clog) or "No changes",
        "preview": preview,
        "info": TASK_INFO.get(task, ""),
        "details": dup_rows,
    })


@app.post("/upload/<uid>/preprocess/finish")
@login_required
@csrf_protect_api
def upload_preprocess_finish(uid: str):
    p = _paths(uid)
    if not os.path.exists(p["mapped"]):
        return jsonify({"ok": False, "error": "No mapped dataset"}), 404
    try:
        df = pd.read_csv(p["mapped"])
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

    df.to_csv(p["clean"], index=False)
    eda_payload = build_eda_payload(df)

    log_path = p["pre_log"]
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        log = data.get("log", [])
        orig_rows = data.get("orig_rows", len(df))
    else:
        log = []
        orig_rows = len(df)
    log.append({"text": f"Final rows: {len(df)} (from {orig_rows})", "step": "summary"})


    with open(p["eda_json"], "w", encoding="utf-8") as f:
        json.dump({
            "log": log,
            "eda": eda_payload,
            "preview": df.head(20).drop(columns=["patient_name"], errors="ignore").replace({np.nan: None}).to_dict(orient="records"),
        }, f)

    return jsonify({"ok": True})


@app.get("/upload/<uid>/eda")
@login_required
def upload_eda(uid: str):
    p = _paths(uid)
    if not os.path.exists(p["clean"]) and not os.path.exists(p["results"]):
        return render_template(
            "error.html",
            title="Session expired",
            messages=["We couldn't find your dataset. Please upload again."],
        ), 404

    if os.path.exists(p["eda_json"]):
        with open(p["eda_json"], "r", encoding="utf-8") as f:
            payload = json.load(f)

        try:
            eda = payload.get("eda", {})
            if "stats" in eda:
                eda["stats"] = _strip_count_from_stats(eda["stats"])

            # If predictions exist but viz payload is missing status-based plots,
            # rebuild the EDA from results so those charts render.
            needs_viz = False
            if os.path.exists(p["results"]):
                viz = eda.get("viz") or {}

                def _missing(key: str) -> bool:
                    val = viz.get(key)
                    if val is None:
                        return True
                    if isinstance(val, (list, dict)) and len(val) == 0:
                        return True
                    # If a list-based viz has only the "All Patients" series,
                    # treat it as missing so we regenerate charts after
                    # predictions introduce additional groups (e.g. No Disease,
                    # Heart Disease or staged values).
                    if (
                        isinstance(val, list)
                        and key in ("bp_box_by_status", "chol_violin_by_stage")
                        and len(val) <= 1
                    ):
                        return True
                    return False

                if (
                    _missing("bp_box_by_status")
                    or _missing("chol_violin_by_stage")
                    or _missing("bp_hist_by_stage")
                ):
                    needs_viz = True
            if needs_viz:
                try:
                    df_res = pd.read_csv(p["results"])
                    eda = build_eda_payload(df_res)
                    payload["preview"] = (
                        df_res.head(20)
                        .drop(columns=["patient_name"], errors="ignore")
                        .replace({np.nan: None})
                        .to_dict(orient="records")
                    )
                except Exception:
                    pass
            payload["eda"] = eda
            with open(p["eda_json"], "w", encoding="utf-8") as wf:
                json.dump(payload, wf)
        except Exception:
            pass

        has_results = os.path.exists(p["results"])
        raw_log = payload.get("log", [])
        log = []
        for item in raw_log:
            if isinstance(item, dict):
                log.append(item)
            else:
                log.append({"text": item})
        groups = group_cleaning_log(log)

        return render_template(
            "uploads/eda.html",
            uid=uid,
            cleaning_log=log,
            cleaning_groups=groups,
            cleaning_log_json=json.dumps(log),
            preview_json=json.dumps(payload.get("preview", [])),
            eda_json=json.dumps(payload.get("eda", {})),
            outliers_json=json.dumps(payload.get("outliers", [])),
            has_results=has_results,
            banner=None,
        )

    csv_path = p["results"] if os.path.exists(p["results"]) else p["clean"]
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        return render_template(
            "error.html",
            title="Failed to load dataset",
            messages=[f"{type(e).__name__}: {e}"],
        ), 400

    try:
        eda_payload = build_eda_payload(df)
    except Exception as e:
        return render_template("error.html", title="EDA failed",
                               messages=[f"{type(e).__name__}: {e}"]), 500

    preview = (
        df.head(20)
        .drop(columns=["patient_name"], errors="ignore")
        .replace({np.nan: None})
        .to_dict(orient="records")
    )
    cleaning_log = [{"text": "Loaded results dataset" if os.path.exists(p["results"]) else "Loaded cleaned dataset"}, {"text": f"Rows: {len(df)}"}]
    groups = group_cleaning_log(cleaning_log)

    to_save = {"log": cleaning_log, "eda": eda_payload, "preview": preview}
    try:
        with open(p["eda_json"], "w", encoding="utf-8") as f:
            json.dump(to_save, f)
    except Exception as e:
        return render_template("error.html", title="Failed to persist EDA session",
                               messages=[f"{type(e).__name__}: {e}"]), 500

    has_results = os.path.exists(p["results"])
    return render_template(
        "uploads/eda.html",
        uid=uid,
        cleaning_log=cleaning_log,
        cleaning_groups=groups,

        cleaning_log_json=json.dumps(cleaning_log),
        preview_json=json.dumps(preview),
        eda_json=json.dumps(eda_payload),
        outliers_json=json.dumps([]),
        has_results=has_results,
        banner=None
    )


@app.get("/upload/<uid>/preview")
@login_required
def upload_preview(uid: str):
    p = _paths(uid)
    if os.path.exists(p["results"]):
        path = p["results"]
    elif os.path.exists(p["clean"]):
        path = p["clean"]
    else:
        path = p.get("mapped")

    if not path or not os.path.exists(path):
        return jsonify({"error": "not found"}), 404
    start = int(request.args.get("start", 0))
    limit = int(request.args.get("limit", 20))
    try:
        df = pd.read_csv(path)
    except Exception as e:
        return jsonify({"error": f"{type(e).__name__}: {e}"}), 400
    rows = df.iloc[start:start + limit].drop(columns=["patient_name"], errors="ignore").replace({np.nan: None}).to_dict(orient="records")
    return jsonify({"rows": rows})

@app.get("/upload/<uid>/download/clean")
@login_required
def upload_download_clean(uid: str):
    p = _paths(uid)
    if not os.path.exists(p["clean"]):
        return render_template("error.html", title="Not found",
                               messages=["Cleaned dataset not available."]), 404
    return send_file(p["clean"], as_attachment=True, download_name=f"cleaned_{uid}.csv", mimetype="text/csv")

@app.post("/upload/<uid>/predict")
@login_required
@csrf_protect
def upload_predict(uid: str):
    p = _paths(uid)
    if not os.path.exists(p["clean"]):
        return render_template("error.html", title="Not found",
                               messages=["Cleaned dataset not available."]), 404
    try:
        df = pd.read_csv(p["clean"])
    except Exception as e:
        return render_template("error.html", title="Failed to load cleaned CSV",
                               messages=[f"{type(e).__name__}: {e}"]), 400

    if model is None:
        return render_template("error.html", title="Prediction error",
                               messages=["Model not loaded. Place ml/model.pkl and restart."]), 500

    X = df[INPUT_COLUMNS].copy()
    try:
        yhat = model.predict(X)
        pos_prob = model.predict_proba(X)[:, 1] if hasattr(model, "predict_proba") else np.full(len(df), np.nan)
    except Exception as e:
        return render_template("error.html", title="Prediction error",
                               messages=[f"{type(e).__name__}: {e}"]), 500

    df["prediction"] = yhat.astype(int)
    df["positive_probability"] = pos_prob.astype(float)

    inserted_ids = []
    for _, row in df.iterrows():
        prob1 = None if pd.isna(row["positive_probability"]) else float(row["positive_probability"])
        conf = prob1 if int(row["prediction"]) == 1 else (1.0 - prob1) if prob1 is not None else 0.5
        pred = Prediction(
            patient_name=None,
            age=int(row["age"]),
            sex=int(row["sex"]),
            chest_pain_type=str(row["chest_pain_type"]),
            country=(str(row["country"]) if ("country" in df.columns and pd.notna(row.get("country"))) else None),
            resting_bp=float(row["resting_blood_pressure"]),
            cholesterol=float(row["cholesterol"]),
            fasting_blood_sugar=int(row["fasting_blood_sugar"]),
            resting_ecg=str(row["Restecg"]),
            max_heart_rate=float(row["max_heart_rate_achieved"]),
            exercise_angina=int(row["exercise_induced_angina"]),
            oldpeak=float(row["st_depression"]),
            st_slope=str(row["st_slope_type"]),
            num_major_vessels=int(row["num_major_vessels"]),
            thalassemia_type=str(row["thalassemia_type"]),
            prediction=int(row["prediction"]),
            confidence=float(conf),
            model_version=model_name
        )
        db.session.add(pred)
        db.session.flush()
        inserted_ids.append(pred.id)
    db.session.commit()

    df["db_id"] = inserted_ids
    df["confidence"] = np.where(
        df["prediction"] == 1,
        df["positive_probability"],
        1 - df["positive_probability"],
    )
    df.to_csv(p["results"], index=False)

    # Detect numeric outliers (IQR method)
    outliers = []
    num_cols = [
        "age",
        "resting_blood_pressure",
        "cholesterol",
        "max_heart_rate_achieved",
        "st_depression",
        "num_major_vessels",
    ]
    mask = pd.Series(False, index=df.index)
    reasons = [[] for _ in range(len(df))]
    for col in num_cols:
        if col not in df:
            continue
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        low = q1 - 1.5 * iqr
        high = q3 + 1.5 * iqr
        col_mask = (df[col] < low) | (df[col] > high)
        mask |= col_mask
        for idx in df[col_mask].index:
            reasons[idx].append(col)
    out_df = df[mask].copy()
    out_df["outlier_cols"] = [", ".join(reasons[i]) for i in out_df.index]
    out_df = out_df.drop(columns=["patient_name"], errors="ignore")
    outliers = out_df.to_dict(orient="records")


    eda_payload = build_eda_payload(df)
    eda_payload["predicted_distribution"] = {
        "labels": ["No (0)", "Yes (1)"],
        "values": [int((df["prediction"] == 0).sum()), int((df["prediction"] == 1).sum())],
    }
    preview = (
        df.head(20)
        .drop(columns=["patient_name"], errors="ignore")
        .replace({np.nan: None})
        .to_dict(orient="records")
    )
    log = [{"text": f"Predictions added: {len(df)} rows"}]
    to_save = {"log": log, "eda": eda_payload, "preview": preview, "outliers": outliers}
    try:
        with open(p["eda_json"], "w", encoding="utf-8") as f:
            json.dump(to_save, f, indent=2)
    except Exception:
        pass
    groups = group_cleaning_log(log)
    return render_template(
        "uploads/eda.html",
        uid=uid,
        cleaning_log=log,
        cleaning_groups=groups,
        cleaning_log_json=json.dumps(log),

        preview_json=json.dumps(preview),
        eda_json=json.dumps(eda_payload),
        outliers_json=json.dumps(outliers),
        has_results=True,
        banner=f"Batch prediction complete: {len(df)} rows saved.",
        outliers=outliers,
    )

@app.get("/upload/<uid>/download/results")
@login_required
def upload_download_results(uid: str):
    p = _paths(uid)
    if not os.path.exists(p["results"]):
        return render_template("error.html", title="Not found",
                               messages=["No results available. Run predictions first."]), 404
    return send_file(p["results"], as_attachment=True, download_name=f"results_{uid}.csv", mimetype="text/csv")

@app.get("/upload/<uid>/pdf")
@login_required
def upload_bulk_pdf(uid: str):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.pdfgen import canvas

    p = _paths(uid)
    if not os.path.exists(p["results"]):
        return render_template("error.html", title="Not found",
                               messages=["No results available. Run predictions first."]), 404
    df = pd.read_csv(p["results"])
    if "db_id" not in df.columns:
        return render_template("error.html", title="Not found",
                               messages=["Results missing DB ids for PDF."]), 400

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    for _, r in df.iterrows():
        y = height - 2*cm
        c.setFont("Helvetica-Bold", 14)
        c.drawString(2*cm, y, "Heart Disease Prediction Report")
        y -= 1*cm
        c.setFont("Helvetica", 11)

        prob1 = None if pd.isna(r.get("positive_probability")) else float(r["positive_probability"])
        conf = prob1 if int(r["prediction"]) == 1 else (1.0 - prob1) if prob1 is not None else 0.5
        pos_prob_pct = None if prob1 is None else round(prob1*100, 1)
        risk_band = None if prob1 is None else ("Low" if pos_prob_pct < 30 else ("Moderate" if pos_prob_pct < 60 else "High"))

        lines = [
            f"DB ID: {int(r['db_id'])}",
            f"Model Version: {model_name}",
            "",
            f"Age: {int(r['age'])}    Sex: {SEX_MAP.get(int(r['sex']), r['sex'])}",
            f"Country: {str(r.get('country','')) or '-'}",
            f"Chest Pain Type: {str(r['chest_pain_type']).replace('_',' ')}    ST Slope: {str(r['st_slope_type']).replace('_',' ')}",
            f"Resting BP: {float(r['resting_blood_pressure']):.0f} mmHg    Cholesterol: {float(r['cholesterol']):.0f} mg/dL",
            f"FBS ≥120 mg/dL: {YESNO.get(int(r['fasting_blood_sugar']), r['fasting_blood_sugar'])}",
            f"Max HR: {float(r['max_heart_rate_achieved']):.0f} bpm    Exercise Angina: {YESNO.get(int(r['exercise_induced_angina']), r['exercise_induced_angina'])}",
            f"ST Depression: {float(r['st_depression'])}    Rest ECG: {str(r['Restecg']).replace('_',' ')}",
            f"Num Major Vessels: {int(r['num_major_vessels'])}    Thalassemia: {str(r['thalassemia_type']).replace('_',' ')}",
            "",
            f"Prediction: {'HEART DISEASE (Positive)' if int(r['prediction'])==1 else 'No Heart Disease (Negative)'}",
            f"Positive Probability: {'—' if pos_prob_pct is None else f'{pos_prob_pct}%'}",
            f"Risk Band: {risk_band or '—'}",
            f"Confidence: {round(conf*100,1)}%",
        ]
        for line in lines:
            c.drawString(2*cm, y, line)
            y -= 0.8*cm
        c.showPage()

    c.save()
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"batch_report_{uid}.pdf", mimetype="application/pdf")


# ---------------------------
# Entrypoint
# ---------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
