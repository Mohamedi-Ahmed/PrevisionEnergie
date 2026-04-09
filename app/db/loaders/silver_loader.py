from pathlib import Path

import pandas as pd

from app.core.config import BASE_DIR
from app.core.logger import get_logger
from app.db.connection import get_connection
from app.storage.factory import StorageFactory


logger = get_logger(__name__)


UPSERT_COLUMNS = [
    "source_name",
    "date",
    "region",
    "electricity_consumption",
    "gas_consumption",
    "temperature_mean",
    "temperature_min",
    "temperature_max",
    "humidity",
    "wind_speed",
    "precipitation",
    "dju_heating",
    "dju_cooling",
    "year",
    "month",
    "weekday",
    "is_weekend",
    "record_hash",
]


class SilverToSQLLoader:
    def __init__(self, source_name: str) -> None:
        self.source_name = source_name
        self.storage_backend = StorageFactory.create()
        self.upsert_sql = (BASE_DIR / "sql" / "dml" / "upsert_silver.sql").read_text(encoding="utf-8")

    def run(self) -> dict[str, int]:
        silver_dir = f"silver/{self.source_name}"
        silver_files = [
            path
            for path in self.storage_backend.list_files(silver_dir)
            if path.endswith(".csv") and "/quality_reports/" not in path
        ]

        if not silver_files:
            logger.warning("No silver files found for source=%s in %s", self.source_name, silver_dir)
            return {"files_processed": 0, "rows_loaded": 0}

        total_rows_loaded = 0
        for silver_path in silver_files:
            rows_loaded = self._load_file(silver_path)
            total_rows_loaded += rows_loaded
            logger.info("Loaded silver file into SQL | file=%s | rows=%s", silver_path, rows_loaded)

        return {"files_processed": len(silver_files), "rows_loaded": total_rows_loaded}

    def _load_file(self, silver_relative_path: str) -> int:
        content = self.storage_backend.read_bytes(silver_relative_path)
        from io import StringIO
        df = pd.read_csv(StringIO(content.decode("utf-8")))

        if df.empty:
            return 0

        if "source_name" not in df.columns:
            df["source_name"] = self.source_name
        if "record_hash" not in df.columns:
            df["record_hash"] = None

        # Normalize booleans / datetimes / missing values for sqlite upsert
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        if "is_weekend" in df.columns:
            df["is_weekend"] = df["is_weekend"].map(lambda value: int(bool(value)) if pd.notna(value) else None)

        df = df.where(pd.notna(df), None)
        rows = []
        for _, row in df.iterrows():
            payload = {column: row[column] if column in df.columns else None for column in UPSERT_COLUMNS}
            rows.append(payload)

        with get_connection() as connection:
            connection.executemany(self.upsert_sql, rows)
            connection.commit()

        return len(rows)
