from app.core.logger import get_logger
from app.db.loaders.gold_loader import SilverToGoldLoader
from app.db.loaders.silver_loader import SilverToSQLLoader
from app.etl.silver_pipeline import SilverPipeline


logger = get_logger(__name__)


class ETLOrchestrator:
    def __init__(self, source_name: str = "kaggle", enrich_from_api: bool = False, build_gold: bool = False) -> None:
        self.source_name = source_name
        self.enrich_from_api = enrich_from_api
        self.build_gold = build_gold
        self.silver_pipeline = SilverPipeline(source_name=source_name, enrich_from_api=enrich_from_api)
        self.silver_loader = SilverToSQLLoader(source_name=source_name)
        self.gold_loader = SilverToGoldLoader() if build_gold else None

    def run(self) -> dict[str, object]:
        logger.info(
            "ETL orchestration started for source=%s | enrich_from_api=%s | build_gold=%s.",
            self.source_name,
            self.enrich_from_api,
            self.build_gold,
        )
        silver_results = self.silver_pipeline.run()
        load_result = self.silver_loader.run()
        gold_result = self.gold_loader.run() if self.gold_loader is not None else None
        logger.info("ETL orchestration finished for source=%s.", self.source_name)
        return {
            "source_name": self.source_name,
            "enrich_from_api": self.enrich_from_api,
            "build_gold": self.build_gold,
            "silver_files": silver_results,
            "load_result": load_result,
            "gold_result": gold_result,
        }
