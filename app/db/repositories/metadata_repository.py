from app.core.exceptions import DatabaseError
from app.core.logger import get_logger
from app.db.connection import get_connection

logger = get_logger(__name__)


class MetadataRepository:
    def list_regions(self) -> list[str]:
        try:
            query = (
                "SELECT DISTINCT region "
                "FROM silver_energy_weather_daily "
                "WHERE region IS NOT NULL AND TRIM(region) <> '' "
                "ORDER BY region ASC"
            )
            with get_connection() as connection:
                cursor = connection.execute(query)
                rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as exc:
            logger.error("Erreur lors de la requete metadata regions : %s", exc)
            raise DatabaseError(f"Failed to list regions: {exc}") from exc
