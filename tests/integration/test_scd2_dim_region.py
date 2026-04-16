import sqlite3

import pytest

from app.core.config import get_settings
from app.db.loaders.gold_loader import REGION_ENRICHMENT, SilverToGoldLoader
from app.db.sql_runner import SQLRunner


@pytest.fixture()
def scd2_db(tmp_path, monkeypatch):
    db_path = tmp_path / "scd2.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    get_settings.cache_clear()
    SQLRunner().run_directory("sql/ddl")
    yield db_path
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()


def test_dim_region_scd2_closes_previous_version_and_inserts_new_one(scd2_db, monkeypatch) -> None:
    with sqlite3.connect(scd2_db) as connection:
        connection.execute(
            """
            INSERT INTO silver_energy_weather_daily
                (source_name, date, region, electricity_consumption, gas_consumption,
                 temperature_mean, temperature_min, temperature_max,
                 humidity, wind_speed, precipitation, dju_heating, dju_cooling,
                 is_weekend, weekday, month, year, record_hash)
            VALUES
                ('kaggle', '2024-01-01', 'ile-de-france', 100.0, 60.0,
                 5.0, 2.0, 8.0, 70.0, 10.0, 1.0, 13.0, 0.0, 0, 0, 1, 2024, 'a')
            """
        )
        connection.commit()

    loader = SilverToGoldLoader()
    loader.run()

    original = REGION_ENRICHMENT["ile-de-france"].copy()
    monkeypatch.setitem(
        REGION_ENRICHMENT,
        "ile-de-france",
        {
            **original,
            "climate_zone": "hybrid-demo",
        },
    )

    loader.run()

    with sqlite3.connect(scd2_db) as connection:
        rows = connection.execute(
            """
            SELECT region_code, climate_zone, valid_from, valid_to, is_current
            FROM dim_region
            WHERE region_code = 'ile-de-france'
            ORDER BY region_key
            """
        ).fetchall()

    assert len(rows) == 2
    assert rows[0][3] is not None
    assert rows[0][4] == 0
    assert rows[1][1] == "hybrid-demo"
    assert rows[1][4] == 1
    assert rows[0][2] != rows[1][2]
