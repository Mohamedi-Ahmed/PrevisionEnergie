from app.core.config import get_settings
from app.ingestion.api_base import BaseAPIExtractor


class DataGouvExtractor(BaseAPIExtractor):
    source_name = "data_gouv"

    def __init__(self, storage_backend, bronze_subdir: str = "bronze/data_gouv") -> None:
        settings = get_settings()
        super().__init__(
            storage_backend=storage_backend,
            bronze_subdir=bronze_subdir,
            base_url=settings.data_gouv_base_url,
            default_headers={},
            timeout=30.0,
        )
