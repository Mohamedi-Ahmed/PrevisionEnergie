from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse

from app.core.logger import setup_logging
from app.ingestion.kaggle_extractor import KaggleExtractor
from app.storage.factory import StorageFactory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest Kaggle CSV into bronze storage.")
    parser.add_argument("--source-file", dest="source_file_path", help="Path to a local CSV file.")
    parser.add_argument("--source-url", dest="source_url", help="Direct URL to a downloadable file.")
    parser.add_argument("--destination-filename", help="Optional destination filename.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging()
    storage_backend = StorageFactory.create()
    extractor = KaggleExtractor(storage_backend=storage_backend)
    result = extractor.extract(
        source_file_path=args.source_file_path,
        source_url=args.source_url,
        destination_filename=args.destination_filename,
    )
    print(result)


if __name__ == "__main__":
    main()
