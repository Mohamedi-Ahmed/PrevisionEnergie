from fastapi import APIRouter, Depends

from app.api.deps import get_metadata_repository, verify_bearer_token
from app.db.repositories.metadata_repository import MetadataRepository


router = APIRouter(prefix="/api/v1/metadata", tags=["metadata"])


@router.get("/regions", summary="List available regions")
def list_regions(
    _: str = Depends(verify_bearer_token),
    repository: MetadataRepository = Depends(get_metadata_repository),
) -> dict[str, list[str]]:
    return {"regions": repository.list_regions()}
