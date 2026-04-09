from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse
import json

from app.core.logger import setup_logging
from app.ingestion.orchestrator import IngestionOrchestrator



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run ingestion for a specific source.")
    parser.add_argument("source", choices=["kaggle", "rte", "meteo_france", "data_gouv"])
    parser.add_argument("--source-file", dest="source_file_path", help="Local file path for file-based sources.")
    parser.add_argument("--source-url", dest="source_url", help="Remote URL for file-based sources.")
    parser.add_argument("--endpoint", help="API endpoint to call.")
    parser.add_argument("--absolute-url", help="Absolute API URL.")
    parser.add_argument("--params", default="{}", help="JSON string of query parameters.")
    parser.add_argument("--destination-filename", help="Optional destination filename in bronze.")
    return parser.parse_args()



def build_kwargs(args: argparse.Namespace) -> dict:
    if args.source == "kaggle":
        return {
            key: value
            for key, value in {
                "source_file_path": args.source_file_path,
                "source_url": args.source_url,
                "destination_filename": args.destination_filename,
            }.items()
            if value is not None
        }

    return {
        key: value
        for key, value in {
            "endpoint": args.endpoint,
            "absolute_url": args.absolute_url,
            "params": json.loads(args.params),
            "destination_filename": args.destination_filename,
        }.items()
        if value is not None
    }



def main() -> None:
    args = parse_args()
    setup_logging()
    orchestrator = IngestionOrchestrator()
    result = orchestrator.run_source(args.source, **build_kwargs(args))
    print(result)


if __name__ == "__main__":
    main()
