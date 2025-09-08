"""Add email verification support.

Creates email_verification table and email_verified_at column.
Idempotent so it can be safely re-run.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import inspect, text

from app import db, EmailVerification


def run() -> None:
    engine = db.engine
    insp = inspect(engine)

    # Add email_verified_at column to user table
    cols = [c["name"] for c in insp.get_columns("user")]
    if "email_verified_at" not in cols:
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE user ADD COLUMN email_verified_at DATETIME"))
            conn.execute(
                text(
                    "UPDATE user SET email_verified_at = :now WHERE email_verified_at IS NULL"
                ),
                {"now": datetime.utcnow()},
            )

    # Create email_verification table if missing
    if not insp.has_table("email_verification"):
        EmailVerification.__table__.create(engine)


if __name__ == "__main__":
    run()
