from app.core.security import verify_bearer_token
from app.db.repositories.consumption_repository import ConsumptionRepository
from app.db.repositories.feature_repository import FeatureRepository
from app.db.repositories.metadata_repository import MetadataRepository



def get_feature_repository() -> FeatureRepository:
    return FeatureRepository()



def get_consumption_repository() -> ConsumptionRepository:
    return ConsumptionRepository()



def get_metadata_repository() -> MetadataRepository:
    return MetadataRepository()
