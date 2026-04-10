"""
Extracteur meteo via l'API Open-Meteo (gratuite, sans cle).

Recupere les donnees meteo quotidiennes par region francaise :
temperature min/max/moyenne, precipitation, vent, ensoleillement.

Chaque region est representee par les coordonnees de sa capitale regionale.
Les donnees sont stockees en Bronze au format CSV.
"""

from __future__ import annotations

import csv
import io
from typing import Any

from app.core.logger import get_logger
from app.ingestion.base import BaseExtractor, IngestionResult
from app.ingestion.http_client import HTTPIngestionClient
from app.ingestion.utils import build_raw_filename

logger = get_logger(__name__)

# Capitales regionales avec coordonnees GPS
REGIONS: dict[str, tuple[float, float]] = {
    "Ile-de-France": (48.8566, 2.3522),
    "Auvergne-Rhone-Alpes": (45.7640, 4.8357),
    "Bourgogne-Franche-Comte": (47.3220, 6.0833),
    "Bretagne": (48.1173, -1.6778),
    "Centre-Val-de-Loire": (47.9029, 1.9093),
    "Grand-Est": (48.5734, 7.7521),
    "Hauts-de-France": (50.6292, 3.0573),
    "Normandie": (49.1829, -0.3707),
    "Nouvelle-Aquitaine": (44.8378, -0.5792),
    "Occitanie": (43.6047, 1.4442),
    "Pays-de-la-Loire": (47.2184, -1.5536),
    "Provence-Alpes-Cote-d-Azur": (43.2965, 5.3698),
}

OPEN_METEO_URL = "https://archive-api.open-meteo.com/v1/archive"

DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
    "sunshine_duration",
]


class MeteoFranceExtractor(BaseExtractor):
    """Extracteur meteo reel via Open-Meteo Archive API."""

    source_name = "meteo_france"

    def __init__(self, storage_backend, bronze_subdir: str = "bronze/meteo_france") -> None:
        super().__init__(storage_backend=storage_backend, bronze_subdir=bronze_subdir)
        self.client = HTTPIngestionClient(base_url=OPEN_METEO_URL, timeout=30.0)

    def extract(
        self,
        start_date: str = "2023-01-01",
        end_date: str = "2023-12-31",
        regions: list[str] | None = None,
        destination_filename: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> IngestionResult:
        """
        Appelle l'API Open-Meteo pour chaque region et stocke le resultat
        en CSV dans Bronze.
        """
        target_regions = regions or list(REGIONS.keys())
        all_rows: list[dict[str, Any]] = []

        for region_name in target_regions:
            if region_name not in REGIONS:
                logger.warning("Region inconnue, ignoree : %s", region_name)
                continue

            lat, lon = REGIONS[region_name]
            logger.info("Ingestion meteo %s (%s-%s)...", region_name, start_date, end_date)

            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "daily": ",".join(DAILY_VARIABLES),
                "timezone": "Europe/Paris",
            }

            response = self.client.get_json(
                absolute_url=OPEN_METEO_URL,
                params=params,
            )

            daily = response.get("daily", {})
            dates = daily.get("time", [])

            for i, date in enumerate(dates):
                row = {"date": date, "region": region_name}
                for var in DAILY_VARIABLES:
                    values = daily.get(var, [])
                    row[var] = values[i] if i < len(values) else None
                all_rows.append(row)

        # Ecrire en CSV dans Bronze
        output = io.StringIO()
        fieldnames = ["date", "region"] + DAILY_VARIABLES
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)
        content = output.getvalue().encode("utf-8")

        filename = destination_filename or build_raw_filename(
            source_name=self.source_name,
            extension="csv",
        )
        storage_path = f"{self.bronze_subdir}/{filename}"
        self.storage_backend.write_bytes(relative_path=storage_path, content=content)

        logger.info(
            "Ingestion meteo terminee : %d lignes, %d regions",
            len(all_rows),
            len(target_regions),
        )

        return IngestionResult(
            source_name=self.source_name,
            storage_path=storage_path,
            extracted_at=self.now_utc_iso(),
            record_count=len(all_rows),
            content_type="text/csv",
            metadata={
                "start_date": start_date,
                "end_date": end_date,
                "regions": target_regions,
                "api": "Open-Meteo Archive",
                **(metadata or {}),
            },
        )
