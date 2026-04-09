import json
from typing import Any

from app.core.exceptions import IngestionConfigurationError
from app.ingestion.base import BaseExtractor, IngestionResult
from app.ingestion.http_client import HTTPIngestionClient
from app.ingestion.utils import build_raw_filename


class BaseAPIExtractor(BaseExtractor):
    default_extension: str = "json"

    def __init__(
        self,
        storage_backend,
        bronze_subdir: str,
        base_url: str | None = None,
        default_headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        super().__init__(storage_backend=storage_backend, bronze_subdir=bronze_subdir)
        self.client = HTTPIngestionClient(
            base_url=base_url,
            headers=default_headers,
            timeout=timeout,
        )

    def extract(
        self,
        endpoint: str | None = None,
        absolute_url: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        destination_filename: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> IngestionResult:
        if not endpoint and not absolute_url:
            raise IngestionConfigurationError(
                f"{self.source_name} extraction requires either an endpoint or an absolute_url."
            )

        payload = self.client.get_json(
            endpoint=endpoint,
            absolute_url=absolute_url,
            params=params,
            headers=headers,
        )
        content = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        filename = destination_filename or build_raw_filename(
            source_name=self.source_name,
            extension=self.default_extension,
        )
        storage_path = f"{self.bronze_subdir}/{filename}"
        self.storage_backend.write_bytes(relative_path=storage_path, content=content)

        return IngestionResult(
            source_name=self.source_name,
            storage_path=storage_path,
            extracted_at=self.now_utc_iso(),
            content_type="application/json",
            metadata=metadata or {},
        )
