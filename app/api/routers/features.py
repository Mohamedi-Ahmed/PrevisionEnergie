from datetime import date

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_feature_repository, verify_bearer_token
from app.api.schemas.features import FeatureRecord
from app.db.repositories.feature_repository import FeatureRepository


router = APIRouter(prefix="/api/v1/features", tags=["features"])


@router.get(
    "",
    response_model=list[FeatureRecord],
    summary="Get feature dataset",
    description="Returns feature-ready daily records built from the Silver layer.",
)
def get_features(
    start_date: date = Query(..., description="Start date in YYYY-MM-DD format"),
    end_date: date = Query(..., description="End date in YYYY-MM-DD format"),
    region: str | None = Query(default=None, description="Optional region filter"),
    _: str = Depends(verify_bearer_token),
    repository: FeatureRepository = Depends(get_feature_repository),
) -> list[FeatureRecord]:
    rows = repository.fetch_features(
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        region=region,
    )
    return [FeatureRecord(**row) for row in rows]
