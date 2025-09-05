"""Authentication helpers for role-based access control.

This module provides decorators used to restrict view access to users with
specific roles. The helpers rely on :mod:`flask_login`'s ``current_user`` to
check the logged-in user's role.

These utilities are separated from the main application so that they can be
imported wherever needed without creating circular imports.
"""

from __future__ import annotations

from functools import wraps
from typing import Iterable

from flask import abort
from flask_login import current_user


def role_required(roles: Iterable[str]):
    """Ensure the current user possesses one of ``roles``.

    Parameters
    ----------
    roles:
        An iterable of role names allowed to access the decorated route.

    The decorator aborts with ``403 Forbidden`` if the user is not authenticated
    or does not have an appropriate role. Example::

        @role_required(["Admin", "SuperAdmin"])
        def view():
            ...
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            user_roles = set()
            # Support new many-to-many roles via ``current_user.roles``
            if hasattr(current_user, "roles"):
                try:
                    user_roles.update(r.role_name for r in current_user.roles)
                except TypeError:
                    # "roles" may be None or non-iterable; ignore
                    pass
            # Fallback to legacy single ``role`` attribute
            if getattr(current_user, "role", None):
                user_roles.add(current_user.role)
            if not user_roles.intersection(roles):
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


# Backwards compatibility for older imports
# pragma: no cover - thin wrapper

def roles_required(*roles: str):
    return role_required(roles)


def permission_required(permission: str):
    """Ensure the current user possesses ``permission``.

    The decorator inspects all roles associated with the current user and
    aggregates their permissions. If the requested permission is absent,
    ``403 Forbidden`` is raised.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            user_perms = set()
            try:
                for r in current_user.roles:  # type: ignore[attr-defined]
                    if r.permissions:
                        user_perms.update(
                            k for k, v in r.permissions.items() if v
                        )
            except TypeError:
                pass
            if not user_perms and getattr(current_user, "role", None):
                try:
                    from app import Role  # local import to avoid circular

                    role_obj = Role.query.filter_by(
                        role_name=current_user.role
                    ).first()
                    if role_obj and role_obj.permissions:
                        user_perms.update(
                            k for k, v in role_obj.permissions.items() if v
                        )
                except Exception:
                    pass
            if permission not in user_perms:
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


__all__ = ["role_required", "permission_required"]
