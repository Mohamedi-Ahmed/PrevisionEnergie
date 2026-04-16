from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys

try:
    from _bootstrap import bootstrap_project_root
except ModuleNotFoundError:  # pragma: no cover
    from scripts._bootstrap import bootstrap_project_root


PROJECT_DIR = bootstrap_project_root()

from app.core.logger import setup_logging
from app.db.loaders.gold_loader import SilverToGoldLoader
from app.db.loaders.silver_loader import SilverToSQLLoader
from app.ingestion.kaggle_extractor import KaggleExtractor
from app.processing.pipeline import BronzeToSilverProcessor
from app.storage.factory import StorageFactory


DEFAULT_DATASET_PATH = (
    Path.home()
    / ".cache"
    / "kagglehub"
    / "datasets"
    / "ravvvvvvvvvvvv"
    / "france-energy-weather-hourly"
    / "versions"
    / "1"
    / "merged_daily_regional.csv"
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the full local pipeline from the real Kaggle daily regional dataset."
    )
    parser.add_argument(
        "--dataset-path",
        default=str(DEFAULT_DATASET_PATH),
        help="Path to the real Kaggle daily CSV file.",
    )
    parser.add_argument(
        "--destination-filename",
        default="kaggle_real_daily.csv",
        help="Bronze filename used for this pipeline run.",
    )
    parser.add_argument(
        "--skip-reset-db",
        action="store_true",
        help="Keep the existing SQLite database instead of recreating it.",
    )
    return parser.parse_args()


def run_step(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True, cwd=PROJECT_DIR)


def main() -> None:
    args = parse_args()
    dataset_path = Path(args.dataset_path)
    if not dataset_path.exists():
        raise SystemExit(f"Dataset not found: {dataset_path}")

    setup_logging()
    if not args.skip_reset_db:
        run_step("scripts/init_db.py", "--reset")

    storage_backend = StorageFactory.create()
    extractor = KaggleExtractor(storage_backend=storage_backend)
    result = extractor.extract(
        source_file_path=str(dataset_path),
        destination_filename=args.destination_filename,
        metadata={
            "dataset_label": "ravvvvvvvvvvvv/france-energy-weather-hourly",
            "variant": "merged_daily_regional",
        },
    )

    processor = BronzeToSilverProcessor(storage_backend=storage_backend, source_name="kaggle")
    silver_path, quality_path, quality_report = processor.process_file(result.storage_path)

    silver_loader = SilverToSQLLoader(source_name="kaggle")
    silver_rows = silver_loader.load_file(silver_path)

    gold_result = SilverToGoldLoader().run()

    print("=== Real Kaggle pipeline completed ===")
    print(f"Dataset source: {dataset_path}")
    print(f"Bronze path: {result.storage_path}")
    print(f"Silver path: {silver_path}")
    print(f"Quality report: {quality_path}")
    print(f"Bronze rows detected: {result.record_count}")
    print(f"Silver rows loaded into SQL: {silver_rows}")
    print(f"Gold result: {gold_result}")
    print(
        "Quality summary: "
        f"rows_initial={quality_report.rows_initial}, "
        f"rows_after_deduplication={quality_report.rows_after_deduplication}, "
        f"duplicates_removed={quality_report.duplicates_removed}"
    )


if __name__ == "__main__":
    main()
