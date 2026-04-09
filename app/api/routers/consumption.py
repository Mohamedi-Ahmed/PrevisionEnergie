from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_consumption_repository, verify_bearer_token
from app.api.schemas.consumption import ConsumptionRecord
from app.db.repositories.consumption_repository import ConsumptionRepository


router = APIRouter(prefix="/api/v1/consumption", tags=["consumption"])


@router.get(
    "",
    response_model=list[ConsumptionRecord],
    summary="Get daily consumption dataset",
)
def get_consumption(
    region: str = Query(..., description="Target region"),
    start_date: date = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: date = Query(..., description="End date in YYYY-MM-DD format"),
    _: str = Depends(verify_bearer_token),
    repository: ConsumptionRepository = Depends(get_consumption_repository),
) -> list[ConsumptionRecord]:
    rows = repository.fetch_consumption(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        region=region,
    )
    return [ConsumptionRecord(**row) for row in rows]
