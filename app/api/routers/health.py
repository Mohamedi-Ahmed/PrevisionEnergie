from fastapi import APIRouter

from app.api.schemas.common import HealthResponse
from app.core.config import get_settings
from app.db.connection import get_sqlite_database_path


router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Health check")
def healthcheck() -> HealthResponse:
    settings = get_settings()
    db_path = get_sqlite_database_path()
    database_status = "ok" if db_path.exists() else "not_initialized"
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.app_env,
        database=database_status,
    )
