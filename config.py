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
    SIMULATION_FEATURES = {
        "what_if": os.environ.get("SIM_WHAT_IF", "1").lower() not in {"0", "false"},
        "age_projection": os.environ.get("SIM_AGE_PROJECTION", "1").lower()
        not in {"0", "false"},
    }

    # Encryption/KMS flags
    ENCRYPTION_ENABLED = os.environ.get("ENCRYPTION_ENABLED", "0").lower() in {
        "1",
        "true",
    }
    READ_LEGACY_PLAINTEXT = os.environ.get(
        "READ_LEGACY_PLAINTEXT", "1"
    ).lower() in {"1", "true"}
    KMS_PROVIDER = os.environ.get("KMS_PROVIDER", "dev")
    KMS_KEY_ID = os.environ.get("KMS_KEY_ID", "dev-master")
    IDX_KEY_ID = os.environ.get("IDX_KEY_ID", "dev-idx")
    PEPPER = os.environ.get("PEPPER")
    DEV_KMS_MASTER_KEY = os.environ.get("DEV_KMS_MASTER_KEY")
    DEV_KMS_IDX_KEY = os.environ.get("DEV_KMS_IDX_KEY")

    RBAC_STRICT = os.environ.get("RBAC_STRICT", "1").lower() not in {"0", "false"}

    # --- Email / OTP settings ---
    EMAIL_PROVIDER = os.environ.get("EMAIL_PROVIDER", "gmail")
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    MAIL_FROM = os.environ.get("MAIL_FROM", SMTP_USERNAME)
    MAIL_REPLY_TO = os.environ.get("MAIL_REPLY_TO")

    RESET_CODE_TTL = int(os.environ.get("RESET_CODE_TTL", os.environ.get("OTP_TTL_MIN", "10")))
    OTP_TTL_MIN = RESET_CODE_TTL
    OTP_LENGTH = int(os.environ.get("OTP_LENGTH", "6"))
    OTP_MAX_ATTEMPTS = int(os.environ.get("OTP_MAX_ATTEMPTS", "5"))
    RESET_RESEND_COOLDOWN = int(os.environ.get("RESET_RESEND_COOLDOWN", os.environ.get("OTP_RESEND_COOLDOWN_SEC", "30")))
    OTP_RESEND_COOLDOWN_SEC = RESET_RESEND_COOLDOWN

    AUTO_LOGIN_AFTER_RESET = os.environ.get("AUTO_LOGIN_AFTER_RESET", "0").lower() in {"1", "true"}
    MFA_TOTP_ENABLED = os.environ.get("MFA_TOTP_ENABLED", "1").lower() not in {"0", "false"}
    MFA_REMEMBER_DEVICE_DAYS = int(os.environ.get("MFA_REMEMBER_DEVICE_DAYS", "30"))
    MFA_EMAIL_ENABLED = os.environ.get("MFA_EMAIL_ENABLED", "1").lower() not in {"0", "false"}
    MFA_EMAIL_CODE_LENGTH = int(os.environ.get("MFA_EMAIL_CODE_LENGTH", "6"))
    MFA_EMAIL_TTL_MIN = int(os.environ.get("MFA_EMAIL_TTL_MIN", "10"))
    MFA_EMAIL_MAX_ATTEMPTS = int(os.environ.get("MFA_EMAIL_MAX_ATTEMPTS", "5"))
    MFA_EMAIL_RESEND_COOLDOWN_SEC = int(os.environ.get("MFA_EMAIL_RESEND_COOLDOWN_SEC", "30"))
    MFA_EMAIL_DAILY_CAP_PER_USER = int(os.environ.get("MFA_EMAIL_DAILY_CAP_PER_USER", "10"))
    MFA_TRUST_WINDOW_DAYS_TOTP = int(os.environ.get("MFA_TRUST_WINDOW_DAYS_TOTP", "30"))
    MFA_TRUST_WINDOW_DAYS_EMAIL = int(os.environ.get("MFA_TRUST_WINDOW_DAYS_EMAIL", "7"))
    MFA_STEPUP_REQUIRE_TOTP = os.environ.get("MFA_STEPUP_REQUIRE_TOTP", "1").lower() not in {"0", "false"}

    RATE_LIMIT_PER_IP = int(os.environ.get("RATE_LIMIT_PER_IP", "5"))
    RATE_LIMIT_PER_ID = int(os.environ.get("RATE_LIMIT_PER_ID", "5"))

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
