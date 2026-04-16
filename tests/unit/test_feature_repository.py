import sqlite3

import pytest

from app.core.config import get_settings
from app.db.repositories.feature_repository import FeatureRepository
from app.db.sql_runner import SQLRunner


@pytest.fixture()
def feature_db(tmp_path, monkeypatch):
    db_path = tmp_path / "feature_repository.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    get_settings.cache_clear()

    SQLRunner().run_directory("sql/ddl")

    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            INSERT INTO silver_energy_weather_daily
                (source_name, date, region, electricity_consumption, gas_consumption,
                 temperature_mean, temperature_min, temperature_max,
                 humidity, wind_speed, precipitation, dju_heating, dju_cooling,
                 is_weekend, weekday, month, year, record_hash)
            VALUES
                ('kaggle', '2024-01-01', 'idf', 100.0, 60.0, 5.0, 2.0, 8.0, 70.0, 10.0, 1.0, 13.0, 0.0, 0, 0, 1, 2024, 'a'),
                ('kaggle', '2024-01-02', 'idf', 120.0, 65.0, 6.0, 3.0, 9.0, 68.0, 11.0, 0.5, 12.0, 0.0, 0, 1, 1, 2024, 'b'),
                ('kaggle', '2024-01-01', 'occitanie', 90.0, 50.0, 8.0, 5.0, 11.0, 72.0, 7.0, 0.0, 10.0, 0.0, 0, 0, 1, 2024, 'c')
            """
        )
        connection.commit()

    yield db_path

    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()


def test_fetch_features_filters_by_region(feature_db) -> None:
    repository = FeatureRepository()

    rows = repository.fetch_features(
        start_date="2024-01-01",
        end_date="2024-01-31",
        region="idf",
    )

    assert len(rows) == 2
    assert all(row["region"] == "idf" for row in rows)
    assert rows[0]["electricity_lag_1"] is None
    assert rows[1]["electricity_lag_1"] == 100.0


def test_fetch_features_uses_bound_parameters_against_sql_injection(feature_db) -> None:
    repository = FeatureRepository()
    malicious_region = "idf' OR 1=1 --"

    rows = repository.fetch_features(
        start_date="2024-01-01",
        end_date="2024-01-31",
        region=malicious_region,
    )

    assert rows == []

    with sqlite3.connect(feature_db) as connection:
        table_still_exists = connection.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table' AND name = 'silver_energy_weather_daily'
            """
        ).fetchone()[0]

    assert table_still_exists == 1
