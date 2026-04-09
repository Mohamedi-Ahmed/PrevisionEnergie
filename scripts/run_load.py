from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse

from app.core.logger import setup_logging
from app.db.loaders.silver_loader import SilverToSQLLoader



def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load Silver files into the SQL database.")
    parser.add_argument("--source", required=True, choices=["kaggle", "rte", "meteo_france", "data_gouv"])
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    setup_logging()
    loader = SilverToSQLLoader(source_name=args.source)
    result = loader.run()
    print(result)


if __name__ == "__main__":
    main()
