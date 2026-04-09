from typing import Any

from app.core.config import BASE_DIR
from app.core.exceptions import DatabaseError
from app.core.logger import get_logger
from app.db.connection import get_connection

logger = get_logger(__name__)


class FeatureRepository:
    def __init__(self) -> None:
        self.query_path = BASE_DIR / "sql" / "queries" / "feature_aggregations.sql"

    def _load_query(self) -> str:
        return self.query_path.read_text(encoding="utf-8")

    def fetch_features(self, start_date: str, end_date: str, region: str | None = None) -> list[dict[str, Any]]:
        try:
            sql = self._load_query()
            params = {
                "start_date": start_date,
                "end_date": end_date,
                "region": region,
            }
            with get_connection() as connection:
                cursor = connection.execute(sql, params)
                rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except FileNotFoundError:
            logger.error("Fichier SQL introuvable : %s", self.query_path)
            raise DatabaseError(f"Query file not found: {self.query_path}")
        except Exception as exc:
            logger.error("Erreur lors de la requete features : %s", exc)
            raise DatabaseError(f"Failed to fetch feature data: {exc}") from exc
