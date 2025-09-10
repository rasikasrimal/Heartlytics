from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Shared extensions

db = SQLAlchemy()
login_manager = LoginManager()

__all__ = ["db", "login_manager"]
