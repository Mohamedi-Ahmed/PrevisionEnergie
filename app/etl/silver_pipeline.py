from app.core.logger import get_logger
from app.processing.pipeline import BronzeToSilverProcessor
from app.storage.factory import StorageFactory


logger = get_logger(__name__)


class SilverPipeline:
    def __init__(self, source_name: str, enrich_from_api: bool = False) -> None:
        self.source_name = source_name
        self.enrich_from_api = enrich_from_api
        self.storage_backend = StorageFactory.create()
        self.processor = BronzeToSilverProcessor(
            storage_backend=self.storage_backend,
            source_name=source_name,
            enrich_from_api=enrich_from_api,
        )

    def run(self) -> list[dict[str, str]]:
        bronze_dir = f"bronze/{self.source_name}"
        bronze_files = self.storage_backend.list_files(bronze_dir)
        results: list[dict[str, str]] = []

        if not bronze_files:
            logger.warning("No bronze files found for source=%s in %s", self.source_name, bronze_dir)
            return results

        for bronze_relative_path in bronze_files:
            if bronze_relative_path.endswith(".gitkeep"):
                continue
            logger.info(
                "Processing bronze file=%s | enrich_from_api=%s",
                bronze_relative_path,
                self.enrich_from_api,
            )
            silver_path, quality_path, _ = self.processor.process_file(bronze_relative_path=bronze_relative_path)
            results.append(
                {
                    "bronze_path": bronze_relative_path,
                    "silver_path": silver_path,
                    "quality_report_path": quality_path or "",
                }
            )

        logger.info("Silver pipeline completed for source=%s processed_files=%s", self.source_name, len(results))
        return results
