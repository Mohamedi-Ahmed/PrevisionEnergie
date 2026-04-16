from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import json
from pathlib import Path

from app.core.logger import setup_logging
from app.db.connection import get_connection


BASE_DIR = Path(__file__).resolve().parents[1]


def table_count(connection, table_name: str) -> int:
    return connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]


def main() -> None:
    setup_logging()
    print("DWH local summary")
    with get_connection() as connection:
        for table_name in [
            "dim_date",
            "dim_region",
            "dim_energy",
            "dim_weather_context",
            "fact_energy_consumption_daily",
            "gold_daily_features",
        ]:
            try:
                print(f"{table_name}: {table_count(connection, table_name)} rows")
            except Exception as exc:
                print(f"{table_name}: unavailable ({exc})")

    atlas_bundle = BASE_DIR / "atlas" / "atlas_bundle.json"
    print(f"atlas_bundle_exists: {atlas_bundle.exists()}")
    if atlas_bundle.exists():
        payload = json.loads(atlas_bundle.read_text(encoding='utf-8'))
        print(f"atlas_sections: {', '.join(payload.keys())}")

    print("reference_files:")
    for relative_path in [
        "docs/block3_dwh.md",
        "docs/block3_governance.md",
        "docs/bloc3_referential_mapping.md",
    ]:
        exists = (BASE_DIR / relative_path).exists()
        print(f"- {relative_path} | exists={exists}")


if __name__ == "__main__":
    main()
