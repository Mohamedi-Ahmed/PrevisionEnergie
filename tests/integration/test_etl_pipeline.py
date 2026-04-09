import sqlite3
from pathlib import Path

import pytest

from app.core.config import BASE_DIR
from app.db.sql_runner import SQLRunner
from app.db.loaders.gold_loader import SilverToGoldLoader


@pytest.fixture()
def fresh_db(tmp_path):
    """Cree une base SQLite temporaire avec le schema complet."""
    import os
    db_path = tmp_path / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

    from app.core.config import get_settings
    get_settings.cache_clear()

    runner = SQLRunner()
    runner.run_directory("sql/ddl")
    yield db_path

    os.environ.pop("DATABASE_URL", None)
    get_settings.cache_clear()


def test_ddl_creates_all_tables(fresh_db):
    """Verifie que toutes les tables Gold sont creees."""
    conn = sqlite3.connect(fresh_db)
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    expected = {
        "bronze_ingestion_log",
        "silver_energy_weather_daily",
        "dim_date",
        "dim_region",
        "dim_energy",
        "dim_weather_context",
        "fact_energy_consumption_daily",
        "gold_daily_features",
    }
    assert expected.issubset(tables), f"Tables manquantes : {expected - tables}"


def test_gold_loader_empty_silver(fresh_db):
    """Le Gold loader gere proprement une table Silver vide."""
    loader = SilverToGoldLoader()
    result = loader.run()
    assert result["fact_rows"] == 0
    assert result["dim_date_rows"] == 0


def test_gold_loader_idempotent(fresh_db):
    """Rejouer le Gold loader produit le meme resultat (idempotence)."""
    conn = sqlite3.connect(fresh_db)
    conn.execute(
        """
        INSERT INTO silver_energy_weather_daily
            (source_name, date, region, electricity_consumption, gas_consumption,
             temperature_mean, temperature_min, temperature_max,
             humidity, wind_speed, precipitation, dju_heating, dju_cooling,
             is_weekend, month, year)
        VALUES
            ('kaggle', '2024-01-15', 'ile-de-france', 12000, 8000,
             5.2, 1.0, 9.4, 75, 20, 3.5, 12.8, 0.0, 0, 1, 2024),
            ('kaggle', '2024-01-16', 'ile-de-france', 11500, 7800,
             6.1, 2.0, 10.2, 70, 15, 1.2, 11.9, 0.0, 0, 1, 2024)
        """
    )
    conn.commit()
    conn.close()

    loader = SilverToGoldLoader()
    result1 = loader.run()
    result2 = loader.run()

    assert result1["fact_rows"] == result2["fact_rows"]
    assert result1["dim_date_rows"] == result2["dim_date_rows"]
