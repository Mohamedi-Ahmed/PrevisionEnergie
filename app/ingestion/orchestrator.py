from typing import Any

from app.core.logger import get_logger
from app.ingestion.data_gouv_extractor import DataGouvExtractor
from app.ingestion.kaggle_extractor import KaggleExtractor
from app.ingestion.meteo_france_extractor import MeteoFranceExtractor
from app.ingestion.rte_extractor import RTEExtractor
from app.storage.factory import StorageFactory


logger = get_logger(__name__)


class IngestionOrchestrator:
    def __init__(self) -> None:
        storage_backend = StorageFactory.create()
        self.extractors = {
            "kaggle": KaggleExtractor(storage_backend=storage_backend),
            "rte": RTEExtractor(storage_backend=storage_backend),
            "meteo_france": MeteoFranceExtractor(storage_backend=storage_backend),
            "data_gouv": DataGouvExtractor(storage_backend=storage_backend),
        }

    def run_source(self, source_name: str, **kwargs: Any):
        extractor = self.extractors[source_name]
        logger.info("Starting ingestion for source=%s", source_name)
        result = extractor.extract(**kwargs)
        logger.info("Ingestion completed for source=%s storage_path=%s", source_name, result.storage_path)
        return result

    def run(self) -> None:
        logger.info("Ingestion orchestrator is ready. Use run_source(...) to ingest a specific source.")
