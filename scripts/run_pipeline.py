from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

try:
    from _bootstrap import bootstrap_project_root
except ModuleNotFoundError:  # pragma: no cover
    from scripts._bootstrap import bootstrap_project_root

PROJECT_DIR = bootstrap_project_root()

from app.db.connection import get_sqlite_database_path
from app.core.logger import setup_logging
from app.ingestion.orchestrator import IngestionOrchestrator


def run_step(*args: str) -> None:
    try:
        subprocess.run([sys.executable, *args], check=True, cwd=PROJECT_DIR)
    except subprocess.CalledProcessError as exc:
        command = " ".join(args)
        raise SystemExit(
            f"Command failed during the pipeline run: {command}. "
            "If SQLite is locked, stop the API or any DB viewer and retry."
        ) from exc


def table_count(db_path: Path, table_name: str) -> int:
    with sqlite3.connect(db_path) as connection:
        return connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the local demo pipeline, optionally with fresh Kaggle + API extraction."
    )
    parser.add_argument(
        "--reset-db",
        action="store_true",
        default=True,
        help="Delete and recreate the SQLite demo database before running the pipeline.",
    )
    parser.add_argument(
        "--skip-reset-db",
        action="store_false",
        dest="reset_db",
        help="Keep the existing SQLite database instead of recreating it.",
    )
    parser.add_argument("--kaggle-source-file", help="Optional local Kaggle CSV path to ingest before the ETL.")
    parser.add_argument("--kaggle-source-url", help="Optional remote Kaggle CSV URL to ingest before the ETL.")
    parser.add_argument(
        "--api-source",
        choices=["rte", "meteo_france", "data_gouv"],
        help="Optional API source to ingest before the ETL.",
    )
    parser.add_argument("--api-endpoint", help="Relative endpoint for the optional API source.")
    parser.add_argument("--api-absolute-url", help="Absolute URL for the optional API source.")
    parser.add_argument("--api-params", default="{}", help="JSON string of query parameters for the optional API.")
    parser.add_argument(
        "--skip-gold",
        action="store_true",
        help="Stop after the Silver->SQL load, without rebuilding the Gold layer or manifests.",
    )
    return parser.parse_args()


def should_run_extraction(args: argparse.Namespace) -> bool:
    return any(
        [
            args.kaggle_source_file,
            args.kaggle_source_url,
            args.api_source,
            args.api_endpoint,
            args.api_absolute_url,
        ]
    )


def validate_args(args: argparse.Namespace) -> None:
    if (args.api_endpoint or args.api_absolute_url) and not args.api_source:
        raise SystemExit("Specify --api-source when using --api-endpoint or --api-absolute-url.")
    if args.api_source and not (args.api_endpoint or args.api_absolute_url):
        raise SystemExit("Specify --api-endpoint or --api-absolute-url when using --api-source.")


def ingest_sources(args: argparse.Namespace) -> list[dict[str, object]]:
    setup_logging()
    orchestrator = IngestionOrchestrator()
    results: list[dict[str, object]] = []

    if args.kaggle_source_file or args.kaggle_source_url:
        kaggle_result = orchestrator.run_source(
            "kaggle",
            **{
                key: value
                for key, value in {
                    "source_file_path": args.kaggle_source_file,
                    "source_url": args.kaggle_source_url,
                }.items()
                if value is not None
            },
        )
        results.append(
            {
                "source": "kaggle",
                "storage_path": kaggle_result.storage_path,
                "record_count": kaggle_result.record_count,
            }
        )

    if args.api_source:
        api_kwargs = {
            key: value
            for key, value in {
                "endpoint": args.api_endpoint,
                "absolute_url": args.api_absolute_url,
                "params": json.loads(args.api_params),
            }.items()
            if value is not None
        }
        api_result = orchestrator.run_source(args.api_source, **api_kwargs)
        results.append(
            {
                "source": args.api_source,
                "storage_path": api_result.storage_path,
                "record_count": api_result.record_count,
            }
        )

    return results


def derive_silver_path(source_name: str, bronze_relative_path: str) -> str:
    return f"silver/{source_name}/silver_{Path(bronze_relative_path).stem}.csv"


def build_transform_args(
    args: argparse.Namespace,
    bronze_relative_paths: list[str] | None = None,
) -> list[str]:
    command = ["scripts/run_transform.py", "--source", "kaggle"]
    if args.api_source:
        command.append("--enrich-from-api")
    for bronze_path in bronze_relative_paths or []:
        command.extend(["--bronze-path", bronze_path])
    return command


def build_load_args(silver_relative_paths: list[str] | None = None) -> list[str]:
    command = ["scripts/run_load.py", "--source", "kaggle"]
    for silver_path in silver_relative_paths or []:
        command.extend(["--silver-path", silver_path])
    return command


def main() -> None:
    args = parse_args()
    validate_args(args)
    print("Lancement du pipeline complet...")

    if args.reset_db:
        run_step("scripts/init_db.py", "--reset")
    else:
        run_step("scripts/init_db.py")

    extraction_results: list[dict[str, object]] = []
    if should_run_extraction(args):
        extraction_results = ingest_sources(args)
        print("=== Extraction summary ===")
        for result in extraction_results:
            print(
                f"{result['source']}: path={result['storage_path']} rows={result['record_count']}"
            )

    kaggle_bronze_paths = [
        str(result["storage_path"])
        for result in extraction_results
        if result["source"] == "kaggle"
    ]
    silver_paths = [derive_silver_path("kaggle", path) for path in kaggle_bronze_paths]

    run_step(*build_transform_args(args, kaggle_bronze_paths or None))
    run_step(*build_load_args(silver_paths or None))
    if not args.skip_gold:
        run_step("scripts/run_gold.py")
        run_step("scripts/export_atlas_metadata.py")
        run_step("scripts/generate_datalake_manifest.py")

    db_path = get_sqlite_database_path()
    print("=== Pipeline summary ===")
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
    if extraction_results:
        print("- Fresh ingestion sources:", ", ".join(str(result["source"]) for result in extraction_results))
    if not args.skip_gold:
        print("- Atlas bundle:", PROJECT_DIR / "atlas" / "atlas_bundle.json")
        print("- Data Lake manifest:", PROJECT_DIR / "docs" / "datalake_manifest.json")


if __name__ == "__main__":
    main()
