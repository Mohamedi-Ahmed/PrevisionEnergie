from fastapi import APIRouter, Depends

from app.core.security import verify_bearer_token
from app.governance.monitoring import run_all_checks

router = APIRouter(tags=["monitoring"])


@router.get(
    "/monitoring",
    summary="Rapport de monitorage et SLA",
    description=(
        "Exécute les health checks (base, fraîcheur, volumétrie) "
        "et retourne un rapport consolidé avec les indicateurs SLA. "
        "Génère des alertes en cas de rupture de service."
    ),
)
def monitoring_report(_: str = Depends(verify_bearer_token)) -> dict:
    return run_all_checks()
