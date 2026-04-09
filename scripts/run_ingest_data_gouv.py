from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse
import json

from app.core.logger import setup_logging
from app.ingestion.data_gouv_extractor import DataGouvExtractor
from app.storage.factory import StorageFactory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest data.gouv.fr API payload into bronze storage.")
    parser.add_argument("--endpoint", help="Relative endpoint.")
    parser.add_argument("--absolute-url", help="Absolute URL to call.")
    parser.add_argument("--params", default="{}", help="JSON string of query parameters.")
    parser.add_argument("--destination-filename", help="Optional destination filename.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging()
    storage_backend = StorageFactory.create()
    extractor = DataGouvExtractor(storage_backend=storage_backend)
    result = extractor.extract(
        endpoint=args.endpoint,
        absolute_url=args.absolute_url,
        params=json.loads(args.params),
        destination_filename=args.destination_filename,
    )
    print(result)


if __name__ == "__main__":
    main()
