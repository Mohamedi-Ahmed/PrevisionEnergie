from app.core.config import get_settings
from app.ingestion.api_base import BaseAPIExtractor


class MeteoFranceExtractor(BaseAPIExtractor):
    source_name = "meteo_france"

    def __init__(self, storage_backend, bronze_subdir: str = "bronze/meteo_france") -> None:
        settings = get_settings()
        headers = {}
        if settings.meteo_france_api_key:
            headers["Authorization"] = f"Bearer {settings.meteo_france_api_key}"
        super().__init__(
            storage_backend=storage_backend,
            bronze_subdir=bronze_subdir,
            base_url=settings.meteo_france_api_base_url,
            default_headers=headers,
            timeout=30.0,
        )
