"""
Vercel Python entrypoint that mounts the existing Flask app.

This file allows deploying the Flask app in `app.py` as a Vercel
Serverless Function. Vercel detects `app` as a WSGI application.
"""

from app import app as app  # Flask application instance defined in app.py

