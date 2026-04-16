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


def get_expiration_date(zone: str, dataset_date: date) -> date | None:
    policy = get_zone_policy(zone)
    retention_years = policy.get("retention_years")
    if retention_years is None:
        return None
    try:
        return dataset_date.replace(year=dataset_date.year + retention_years)
    except ValueError:
        return dataset_date.replace(month=2, day=28, year=dataset_date.year + retention_years)


def should_expire(zone: str, dataset_date: date, reference_date: date) -> bool:
    expiration_date = get_expiration_date(zone, dataset_date)
    if expiration_date is None:
        return False
    return reference_date >= expiration_date
