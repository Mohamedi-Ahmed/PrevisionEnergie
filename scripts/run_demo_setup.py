from __future__ import annotations

from pathlib import Path
import sqlite3
import subprocess
import sys

from _bootstrap import bootstrap_project_root

PROJECT_DIR = bootstrap_project_root()


def run_step(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True, cwd=PROJECT_DIR)


def table_count(db_path: Path, table_name: str) -> int:
    with sqlite3.connect(db_path) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]


def main() -> None:
    print("Preparing local demo environment...")
    run_step("scripts/init_db.py")
    run_step("scripts/run_transform.py", "--source", "kaggle")
    run_step("scripts/run_load.py", "--source", "kaggle")
    run_step("scripts/run_gold.py")
    run_step("scripts/export_atlas_metadata.py")
    run_step("scripts/generate_datalake_manifest.py")

    db_path = PROJECT_DIR / "energy_forecast.db"
    print("=== Demo-ready summary ===")
    for table_name in [
        "silver_energy_weather_daily",
        "dim_date",
        "dim_region",
        "dim_energy",
        "dim_weather_context",
        "fact_energy_consumption_daily",
        "gold_daily_features",
    ]:
        print(f"{table_name}: {table_count(db_path, table_name)} rows")

    print("Artifacts:")
    print("- DB:", db_path)
    print("- Atlas bundle:", PROJECT_DIR / "atlas" / "atlas_bundle.json")
    print("- Data Lake manifest:", PROJECT_DIR / "docs" / "datalake_manifest.json")


if __name__ == "__main__":
    main()
