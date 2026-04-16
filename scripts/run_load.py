from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse

from app.core.logger import setup_logging
from app.db.loaders.silver_loader import SilverToSQLLoader



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load Silver files into the SQL database.")
    parser.add_argument("--source", required=True, choices=["kaggle", "rte", "meteo_france", "data_gouv"])
    parser.add_argument(
        "--silver-path",
        action="append",
        dest="silver_paths",
        help="Optional silver relative path to load. Repeat the flag to target multiple files.",
    )
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    setup_logging()
    loader = SilverToSQLLoader(source_name=args.source)
    result = loader.run(silver_relative_paths=args.silver_paths)
    print(result)


if __name__ == "__main__":
    main()
