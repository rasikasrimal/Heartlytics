import os
import secrets
from pathlib import Path

# python-dotenv is an optional dependency; gracefully skip if missing.
try:  # pragma: no cover - simple import guard
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - only triggered when dotenv not installed
    def load_dotenv(*args, **kwargs):
        """Fallback no-op if python-dotenv is unavailable."""
        return None

BASE_DIR = Path(__file__).resolve().parent
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", secrets.token_hex(32))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URI", f"sqlite:///{BASE_DIR / 'instance' / 'app.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODEL_PATH = os.environ.get("MODEL_PATH", str(BASE_DIR / 'ml' / 'model.pkl'))
    AVATAR_UPLOAD_FOLDER = os.environ.get(
        "AVATAR_UPLOAD_FOLDER", str(BASE_DIR / "static" / "avatars")
    )
    # Cache-busting version for logo; updated when SuperAdmin changes the logo
    LOGO_VERSION = os.environ.get("LOGO_VERSION", "1")
    ENABLE_WHAT_IF = True
    ENABLE_AGE_PROJECTION = True
    ENABLE_LIFESTYLE_IMPACT = True

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
