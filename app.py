"""Compatibility wrapper for the Heartlytics application package."""

from heartlytics import create_app, db, models, app as application

# Re-export the application instance and common models
app = application
User = models.User
Patient = models.Patient

__all__ = ["app", "create_app", "db", "User", "Patient"]
