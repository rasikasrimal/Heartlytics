from __future__ import annotations

"""Simple role-based access control helpers."""

from enum import Enum
from typing import Iterable

class Role(str, Enum):
    SUPERADMIN = "SuperAdmin"
    ADMIN = "Admin"
    DOCTOR = "Doctor"
    USER = "User"

# Policy mapping modules to allowed roles
POLICY = {
    "Predict": {Role.SUPERADMIN, Role.DOCTOR, Role.USER},
    "Batch": {Role.SUPERADMIN, Role.DOCTOR},
    "Dashboard": {Role.SUPERADMIN, Role.DOCTOR},
    "Research": {Role.SUPERADMIN, Role.DOCTOR},
    "Simulations": {Role.SUPERADMIN},
    "Admin": {Role.SUPERADMIN, Role.ADMIN},
}


def is_superadmin(user) -> bool:
    """Return True if the given user has the SuperAdmin role."""
    return getattr(user, "role", None) == Role.SUPERADMIN.value


def rbac_can(user, module_name: str, action: str = "view") -> bool:
    """Return True if ``user`` is allowed to access ``module_name``."""
    if is_superadmin(user):
        return True
    allowed = POLICY.get(module_name, set())
    return getattr(user, "role", None) in {r.value for r in allowed}
