from datetime import date

from app.governance.lifecycle import get_zone_policy, should_expire


def test_curated_retention_is_five_years():
    assert get_zone_policy("curated")["retention_years"] == 5


def test_consumption_dataset_should_expire():
    assert should_expire("consumption", date(2021, 1, 1), date(2025, 1, 1)) is True
