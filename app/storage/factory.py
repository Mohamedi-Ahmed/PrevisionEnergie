from app.core.config import get_settings
from app.storage.base import StorageBackend
from app.storage.gcs import GCSStorageBackend
from app.storage.local import LocalStorageBackend


class StorageFactory:
    @staticmethod
    def create() -> StorageBackend:
        settings = get_settings()

        if settings.storage_backend == "local":
            return LocalStorageBackend(settings.local_data_dir)

        if settings.storage_backend == "gcs":
            raise ValueError(
                "GCS backend requires additional parameters. Use StorageFactory.create_gcs(...) explicitly."
            )

        raise ValueError(f"Unsupported storage backend: {settings.storage_backend}")

    @staticmethod
    def create_gcs(bucket_name: str, project_id: str | None = None) -> StorageBackend:
        return GCSStorageBackend(bucket_name=bucket_name, project_id=project_id)
