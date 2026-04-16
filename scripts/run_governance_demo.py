from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse
import json
import sqlite3
from pathlib import Path

from app.db.connection import get_sqlite_database_path
from app.governance.lifecycle import get_retention_policy
from app.governance.monitoring import get_sla_config, run_all_checks
from app.governance.rbac import ROLE_PERMISSIONS, get_zone_access_matrix


def _count_current_regions(db_path: Path) -> int | None:
    if not db_path.exists():
        return None
    with sqlite3.connect(db_path) as connection:
        try:
            return connection.execute(
                "SELECT COUNT(*) FROM dim_region WHERE is_current = 1"
            ).fetchone()[0]
        except sqlite3.Error:
            return None


def _count_fact_rows(db_path: Path) -> int | None:
    if not db_path.exists():
        return None
    with sqlite3.connect(db_path) as connection:
        try:
            return connection.execute(
                "SELECT COUNT(*) FROM fact_energy_consumption_daily"
            ).fetchone()[0]
        except sqlite3.Error:
            return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local governance and lifecycle demo with optional monitoring thresholds."
    )
    parser.add_argument(
        "--demo-volume-threshold",
        type=int,
        help="Optional override for the Gold fact row count threshold during the local demo.",
    )
    return parser.parse_args()


def _resolve_volume_override(
    db_path: Path,
    cli_override: int | None,
) -> tuple[int | None, str | None]:
    if cli_override is not None:
        return cli_override, "manual"

    configured_threshold = int(get_sla_config().get("gold_min_row_count", 5))
    fact_rows = _count_fact_rows(db_path)
    if fact_rows is not None and 0 < fact_rows < configured_threshold and fact_rows <= 10:
        return 1, "micro_demo"

    return None, None


def main() -> None:
    args = parse_args()
    project_dir = Path(__file__).resolve().parents[1]
    db_path = get_sqlite_database_path()
    atlas_bundle = project_dir / "atlas" / "atlas_bundle.json"
    manifest_path = project_dir / "docs" / "datalake_manifest.json"
    volume_override, override_reason = _resolve_volume_override(
        db_path,
        args.demo_volume_threshold,
    )
    monitoring_report = run_all_checks(db_path, min_rows_override=volume_override)

    print("Governance & lifecycle demo")
    print("SCD2 dim_region current rows:", _count_current_regions(db_path))
    print("RBAC roles:", ", ".join(sorted(ROLE_PERMISSIONS.keys())))
    print("Zone access matrix:", json.dumps(get_zone_access_matrix(), ensure_ascii=False))
    print("Retention policy:", json.dumps(get_retention_policy(), ensure_ascii=False))
    print("Atlas bundle exists:", atlas_bundle.exists())
    print("Manifest exists:", manifest_path.exists())
    print("Monitoring report:", json.dumps(monitoring_report, ensure_ascii=False))
    if override_reason == "manual":
        print(
            "Demo note: monitoring volume threshold overridden to",
            volume_override,
            "from the command line.",
        )
    elif override_reason == "micro_demo":
        print(
            "Demo note: tiny local dataset detected, monitoring volume threshold adapted to",
            volume_override,
            "for this walkthrough.",
        )


if __name__ == "__main__":
    main()
