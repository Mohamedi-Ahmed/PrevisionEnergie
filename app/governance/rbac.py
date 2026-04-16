from __future__ import annotations

from typing import Final

from app.core.config import get_settings

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


def get_zone_access_matrix() -> dict[str, dict[str, object]]:
    settings = get_settings()
    config = settings.load_yaml("datalake.yaml")
    zones = config.get("datalake", {}).get("zones", {})
    return {
        zone_name: {
            "owner_role": zone_data.get("owner_role"),
            "reader_roles": zone_data.get("reader_roles", []),
            "logical_layer": zone_data.get("logical_layer"),
            "physical_path": zone_data.get("physical_path"),
        }
        for zone_name, zone_data in zones.items()
    }


def can_access_zone(role: str, zone: str, action: str = "read") -> bool:
    permissions = get_role_permissions(role)
    return zone in permissions.get(action, [])
