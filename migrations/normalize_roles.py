"""Idempotent script to normalize legacy roles to supported values."""

from app import db, User
from auth.rbac import Role

def run():
    valid = {r.value for r in Role}
    for user in User.query.all():
        if user.role not in valid:
            user.role = Role.USER.value
    db.session.commit()
    if not User.query.filter_by(role=Role.SUPERADMIN.value).first():
        # Promote first user to SuperAdmin if none exists
        u = User.query.first()
        if u:
            u.role = Role.SUPERADMIN.value
            db.session.commit()

if __name__ == "__main__":
    run()
