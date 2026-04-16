import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import BASE_DIR
from app.core.logger import get_logger
from app.db.connection import get_connection
from app.storage.base import StorageBackend


logger = get_logger(__name__)


@dataclass(slots=True)
class IngestionResult:
    source_name: str
    storage_path: str
    extracted_at: str
    record_count: int | None = None
    content_type: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseExtractor(ABC):
    source_name: str = "unknown"

    def __init__(self, storage_backend: StorageBackend, bronze_subdir: str) -> None:
        self.storage_backend = storage_backend
        self.bronze_subdir = bronze_subdir

    @staticmethod
    def now_utc_iso() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def estimate_csv_record_count(content: bytes) -> int | None:
        try:
            lines = content.decode("utf-8").splitlines()
        except UnicodeDecodeError:
            return None
        if not lines:
            return 0
        return max(len(lines) - 1, 0)

    def write_bronze_file(
        self,
        storage_path: str,
        content: bytes,
        *,
        extracted_at: str,
        record_count: int | None = None,
        load_status: str = "INGESTED",
    ) -> None:
        self.storage_backend.write_bytes(relative_path=storage_path, content=content)
        self._persist_bronze_log(
            storage_path=storage_path,
            content=content,
            extracted_at=extracted_at,
            record_count=record_count,
            load_status=load_status,
        )

    def _persist_bronze_log(
        self,
        *,
        storage_path: str,
        content: bytes,
        extracted_at: str,
        record_count: int | None,
        load_status: str,
    ) -> None:
        self._ensure_bronze_log_table()
        insert_sql = (BASE_DIR / "sql" / "dml" / "insert_bronze.sql").read_text(encoding="utf-8")
        file_path = Path(storage_path)
        payload = {
            "source_name": self.source_name,
            "storage_path": storage_path,
            "file_name": file_path.name,
            "file_extension": file_path.suffix.lower() or None,
            "row_count": record_count,
            "content_hash": hashlib.md5(content).hexdigest(),
            "load_status": load_status,
            "extracted_at": extracted_at,
        }
        with get_connection() as connection:
            connection.execute(insert_sql, payload)
            connection.commit()

    @staticmethod
    def _ensure_bronze_log_table() -> None:
        ddl_sql = (BASE_DIR / "sql" / "ddl" / "create_bronze_tables.sql").read_text(encoding="utf-8")
        with get_connection() as connection:
            connection.executescript(ddl_sql)
            connection.commit()

    @abstractmethod
    def extract(self, **kwargs: Any) -> IngestionResult:
        raise NotImplementedError
