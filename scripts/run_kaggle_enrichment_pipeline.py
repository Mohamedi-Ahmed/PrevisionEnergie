from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse
import json

from app.core.logger import setup_logging
from app.etl.orchestrator import ETLOrchestrator
from app.ingestion.orchestrator import IngestionOrchestrator



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Kaggle + optional APIs, then enrich and load.")
    parser.add_argument("--kaggle-source-file", required=True, help="Local Kaggle CSV path")
    parser.add_argument("--rte-endpoint", help="Optional RTE endpoint")
    parser.add_argument("--rte-absolute-url", help="Optional RTE absolute URL")
    parser.add_argument("--rte-params", default="{}", help="Optional JSON params for RTE")
    parser.add_argument("--meteo-endpoint", help="Optional Météo-France endpoint")
    parser.add_argument("--meteo-absolute-url", help="Optional Météo-France absolute URL")
    parser.add_argument("--meteo-params", default="{}", help="Optional JSON params for Météo-France")
    parser.add_argument("--data-gouv-endpoint", help="Optional data.gouv.fr endpoint")
    parser.add_argument("--data-gouv-absolute-url", help="Optional data.gouv.fr absolute URL")
    parser.add_argument("--data-gouv-params", default="{}", help="Optional JSON params for data.gouv.fr")
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    setup_logging()

    ingestion = IngestionOrchestrator()
    ingestion.run_source("kaggle", source_file_path=args.kaggle_source_file)

    if args.rte_endpoint or args.rte_absolute_url:
        ingestion.run_source(
            "rte",
            endpoint=args.rte_endpoint,
            absolute_url=args.rte_absolute_url,
            params=json.loads(args.rte_params),
        )

    if args.meteo_endpoint or args.meteo_absolute_url:
        ingestion.run_source(
            "meteo_france",
            endpoint=args.meteo_endpoint,
            absolute_url=args.meteo_absolute_url,
            params=json.loads(args.meteo_params),
        )

    if args.data_gouv_endpoint or args.data_gouv_absolute_url:
        ingestion.run_source(
            "data_gouv",
            endpoint=args.data_gouv_endpoint,
            absolute_url=args.data_gouv_absolute_url,
            params=json.loads(args.data_gouv_params),
        )

    etl = ETLOrchestrator(source_name="kaggle", enrich_from_api=True)
    result = etl.run()
    print(result)


if __name__ == "__main__":
    main()
