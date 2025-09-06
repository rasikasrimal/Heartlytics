from __future__ import annotations

"""Decorators for enforcing RBAC policies."""

from functools import wraps
from flask import abort, current_app, request
from flask_login import current_user

from .rbac import Role, is_superadmin, rbac_can


def require_roles(*roles: str):
    """Allow access only to users with any of ``roles``.
    SuperAdmin bypasses the check.
    """

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if is_superadmin(current_user) or current_user.role in roles:
                return fn(*args, **kwargs)
            current_app.logger.warning(
                "RBAC deny: user=%s role=%s endpoint=%s required=%s",
                getattr(current_user, "id", None),
                getattr(current_user, "role", None),
                request.endpoint,
                roles,
            )
            abort(403)

        return wrapper

    return decorator


def require_module_access(module_name: str, action: str = "view"):
    """Ensure the current user can access ``module_name`` according to policy."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or not rbac_can(
                current_user, module_name, action
            ):
                current_app.logger.warning(
                    "RBAC deny: user=%s role=%s module=%s action=%s",
                    getattr(current_user, "id", None),
                    getattr(current_user, "role", None),
                    module_name,
                    action,
                )
                abort(403)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
