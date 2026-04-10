"""
Ingestion meteo reelle via Open-Meteo API.

Usage :
    python scripts/run_ingest_meteo_france.py
    python scripts/run_ingest_meteo_france.py --start 2024-01-01 --end 2024-12-31
    python scripts/run_ingest_meteo_france.py --regions Ile-de-France Bretagne
"""

from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse

from app.core.logger import setup_logging
from app.ingestion.meteo_france_extractor import MeteoFranceExtractor, REGIONS
from app.storage.factory import StorageFactory


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingestion meteo via Open-Meteo API")
    parser.add_argument("--start", default="2023-01-01", help="Date de debut (YYYY-MM-DD)")
    parser.add_argument("--end", default="2023-12-31", help="Date de fin (YYYY-MM-DD)")
    parser.add_argument("--regions", nargs="*", default=None, help="Regions a ingerer (defaut: toutes)")
    parser.add_argument("--destination-filename", default=None, help="Nom du fichier de sortie")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    setup_logging()
    storage_backend = StorageFactory.create()
    extractor = MeteoFranceExtractor(storage_backend=storage_backend)

    print(f"Ingestion meteo : {args.start} -> {args.end}")
    print(f"Regions : {args.regions or 'toutes (12)'}")
    print()

    result = extractor.extract(
        start_date=args.start,
        end_date=args.end,
        regions=args.regions,
        destination_filename=args.destination_filename,
    )

    print(f"\nResultat :")
    print(f"  Source     : {result.source_name}")
    print(f"  Fichier    : {result.storage_path}")
    print(f"  Lignes     : {result.record_count}")
    print(f"  Date       : {result.extracted_at}")
    print(f"  Metadata   : {result.metadata}")


if __name__ == "__main__":
    main()
