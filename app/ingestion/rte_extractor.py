from app.core.config import get_settings
from app.ingestion.api_base import BaseAPIExtractor


class RTEExtractor(BaseAPIExtractor):
    source_name = "rte"

    def __init__(self, storage_backend, bronze_subdir: str = "bronze/rte") -> None:
        settings = get_settings()
        headers = {}
        if settings.rte_api_key:
            headers["Authorization"] = f"Bearer {settings.rte_api_key}"
        super().__init__(
            storage_backend=storage_backend,
            bronze_subdir=bronze_subdir,
            base_url=settings.rte_api_base_url,
            default_headers=headers,
            timeout=30.0,
        )
