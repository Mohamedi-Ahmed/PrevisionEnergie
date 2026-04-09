from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.storage.base import StorageBackend


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

    @abstractmethod
    def extract(self, **kwargs: Any) -> IngestionResult:
        raise NotImplementedError
