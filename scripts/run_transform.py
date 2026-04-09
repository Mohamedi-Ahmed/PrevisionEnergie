from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse

from app.core.logger import setup_logging
from app.etl.silver_pipeline import SilverPipeline



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Bronze to Silver transformation.")
    parser.add_argument("--source", required=True, choices=["kaggle", "rte", "meteo_france", "data_gouv"])
    parser.add_argument(
        "--enrich-from-api",
        action="store_true",
        help="When source=kaggle, enrich the Kaggle dataset with available API bronze datasets.",
    )
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    setup_logging()
    pipeline = SilverPipeline(source_name=args.source, enrich_from_api=args.enrich_from_api)
    results = pipeline.run()
    print(results)


if __name__ == "__main__":
    main()
