from pathlib import Path
from typing import Any

from app.core.exceptions import IngestionConfigurationError, IngestionError
from app.ingestion.base import BaseExtractor, IngestionResult
from app.ingestion.http_client import HTTPIngestionClient
from app.ingestion.utils import build_raw_filename, infer_extension_from_path


class KaggleExtractor(BaseExtractor):
    """Ingestion strategy for the Kaggle CSV source.

    In Bloc 2, the most realistic and stable workflow is often:
    1. manual or scripted download of the Kaggle file,
    2. ingestion of the raw CSV into Bronze.

    This extractor supports:
    - a local file path (`source_file_path`), or
    - a direct URL (`source_url`) when a downloadable file exists.
    """

    source_name = "kaggle"
    default_extension = "csv"

    def __init__(self, storage_backend, bronze_subdir: str = "bronze/kaggle") -> None:
        super().__init__(storage_backend=storage_backend, bronze_subdir=bronze_subdir)
        self.http_client = HTTPIngestionClient(timeout=60.0)

    def extract(
        self,
        source_file_path: str | None = None,
        source_url: str | None = None,
        destination_filename: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> IngestionResult:
        if not source_file_path and not source_url:
            raise IngestionConfigurationError(
                "Kaggle extraction requires either 'source_file_path' or 'source_url'."
            )

        if source_file_path:
            file_path = Path(source_file_path)
            if not file_path.exists() or not file_path.is_file():
                raise IngestionError(f"Local source file not found: {source_file_path}")
            content = file_path.read_bytes()
            extension = infer_extension_from_path(source_file_path, default=self.default_extension)
        else:
            content = self.http_client.get_bytes(absolute_url=source_url)
            extension = infer_extension_from_path(source_url or "", default=self.default_extension)

        filename = destination_filename or build_raw_filename(
            source_name=self.source_name,
            extension=extension,
        )
        storage_path = f"{self.bronze_subdir}/{filename}"
        self.storage_backend.write_bytes(relative_path=storage_path, content=content)

        payload_metadata = metadata or {}
        if source_file_path:
            payload_metadata.setdefault("source_file_path", source_file_path)
        if source_url:
            payload_metadata.setdefault("source_url", source_url)

        return IngestionResult(
            source_name=self.source_name,
            storage_path=storage_path,
            extracted_at=self.now_utc_iso(),
            content_type="text/csv",
            metadata=payload_metadata,
        )
