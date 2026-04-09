from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse

from app.core.logger import setup_logging
from app.etl.orchestrator import ETLOrchestrator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ETL pipeline.")
    parser.add_argument("--source", default="kaggle", choices=["kaggle", "rte", "meteo_france", "data_gouv"])
    parser.add_argument(
        "--enrich-from-api",
        action="store_true",
        help="When source=kaggle, enrich the Kaggle dataset with available API bronze datasets.",
    )
    parser.add_argument(
        "--build-gold",
        action="store_true",
        help="Build the Bloc 3 Gold DWH star schema after the Silver load.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging()
    orchestrator = ETLOrchestrator(
        source_name=args.source,
        enrich_from_api=args.enrich_from_api,
        build_gold=args.build_gold,
    )
    result = orchestrator.run()
    print(result)


if __name__ == "__main__":
    main()
