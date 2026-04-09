from __future__ import annotations

from typing import Final

ROLE_PERMISSIONS: Final[dict[str, dict[str, list[str]]]] = {
    "data_reader": {
        "read": ["curated", "consumption", "metadata"],
        "write": [],
        "admin": [],
    },
    "data_engineer": {
        "read": ["raw", "curated", "consumption", "metadata"],
        "write": ["raw", "curated", "consumption", "metadata"],
        "admin": [],
    },
    "data_admin": {
        "read": ["raw", "curated", "consumption", "metadata"],
        "write": ["raw", "curated", "consumption", "metadata"],
        "admin": ["raw", "curated", "consumption", "metadata"],
    },
}


def get_role_permissions(role: str) -> dict[str, list[str]]:
    return ROLE_PERMISSIONS.get(role, {"read": [], "write": [], "admin": []})


def can_access_zone(role: str, zone: str, action: str = "read") -> bool:
    permissions = get_role_permissions(role)
    return zone in permissions.get(action, [])
