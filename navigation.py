from __future__ import annotations

"""Navigation configuration and helpers."""

from typing import List, Dict
from auth.rbac import rbac_can

NAV_ITEMS: List[Dict[str, str]] = [
    {"module": "Predict", "label": "Predict", "endpoint": "index", "icon": "bi bi-lightning-charge"},
    {"module": "Batch", "label": "Batch", "endpoint": "upload_form", "icon": "bi bi-upload"},
    {"module": "Dashboard", "label": "Dashboard", "endpoint": "dashboard", "icon": "bi bi-speedometer2"},
    {"module": "Research", "label": "Research", "endpoint": "research_paper", "icon": "bi bi-journal-text"},
    {"module": "Simulations", "label": "Simulations", "endpoint": "simulations.index", "icon": "bi bi-bar-chart"},
    {"module": "Admin", "label": "Admin", "endpoint": "superadmin.dashboard", "icon": "bi bi-gear"},
]

def get_nav_items(user) -> List[Dict[str, str]]:
    """Return nav items allowed for the given user."""
    if not getattr(user, "is_authenticated", False):
        return []
    allowed = []
    for item in NAV_ITEMS:
        if rbac_can(user, item["module"]):
            # handle label override for SuperAdmin label
            if item["module"] == "Admin" and user.role == "SuperAdmin":
                clone = dict(item)
                clone["label"] = "Super Admin"
                allowed.append(clone)
            else:
                allowed.append(item)
    return allowed
