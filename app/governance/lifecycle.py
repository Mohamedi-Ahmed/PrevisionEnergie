from __future__ import annotations

from datetime import date

from app.core.config import get_settings

_DEFAULT_POLICY = {
    "raw": {"retention_years": None, "logical_layer": "bronze"},
    "curated": {"retention_years": 5, "logical_layer": "silver"},
    "consumption": {"retention_years": 2, "logical_layer": "gold"},
}


def _load_policy() -> dict:
    settings = get_settings()
    config = settings.load_yaml("datalake.yaml")
    return config.get("datalake", {}).get("zones", {})


def get_retention_policy() -> dict[str, dict]:
    zones = _load_policy()
    if not zones:
        return _DEFAULT_POLICY
    return {
        zone_name: {
            "retention_years": zone_data.get("retention_years"),
            "logical_layer": zone_data.get("logical_layer"),
            "physical_path": zone_data.get("physical_path"),
        }
        for zone_name, zone_data in zones.items()
    }


def get_zone_policy(zone: str) -> dict:
    return get_retention_policy().get(zone, {})


def should_expire(zone: str, dataset_date: date, reference_date: date) -> bool:
    policy = get_zone_policy(zone)
    retention_years = policy.get("retention_years")
    if retention_years is None:
        return False
    return dataset_date.year <= reference_date.year - retention_years
