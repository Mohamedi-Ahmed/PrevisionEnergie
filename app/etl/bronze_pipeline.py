from app.core.logger import get_logger
from app.ingestion.orchestrator import IngestionOrchestrator


logger = get_logger(__name__)


class BronzePipeline:
    """Orchestre l'ingestion des donnees brutes vers la couche Bronze.

    Chaque source est extraite via son extracteur dedie puis stockee
    dans le repertoire bronze/ du StorageBackend.
    """

    def __init__(self) -> None:
        self.orchestrator = IngestionOrchestrator()

    def run(self, sources: list[str] | None = None) -> dict[str, str]:
        available = list(self.orchestrator.extractors.keys())
        targets = sources or available
        results: dict[str, str] = {}

        for source_name in targets:
            if source_name not in available:
                logger.warning("Source inconnue, ignoree : %s", source_name)
                continue
            try:
                result = self.orchestrator.run_source(source_name)
                results[source_name] = result.storage_path
                logger.info("Bronze OK | source=%s | path=%s", source_name, result.storage_path)
            except Exception as exc:
                logger.error("Bronze ERREUR | source=%s | %s", source_name, exc)
                results[source_name] = f"ERREUR: {exc}"

        logger.info("Bronze pipeline termine | %d/%d sources traitees", len(results), len(targets))
        return results
