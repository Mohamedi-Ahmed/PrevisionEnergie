from typing import Any

from app.core.exceptions import StorageError
from app.storage.base import StorageBackend

try:
    from google.cloud import storage as gcs_storage
except Exception:  # pragma: no cover - optional dependency
    gcs_storage = None


class GCSStorageBackend(StorageBackend):
    """GCS backend skeleton.

    This class is intentionally lightweight for Bloc 2.
    It keeps the contract stable so that switching from local storage
    to Google Cloud Storage later does not impact the ingestion code.
    """

    def __init__(self, bucket_name: str, project_id: str | None = None, credentials: Any | None = None) -> None:
        if gcs_storage is None:
            raise StorageError(
                "google-cloud-storage is not installed. Install it before using the GCS backend."
            )
        self.bucket_name = bucket_name
        self.client = gcs_storage.Client(project=project_id, credentials=credentials)
        self.bucket = self.client.bucket(bucket_name)

    def write_bytes(self, relative_path: str, content: bytes) -> str:
        blob = self.bucket.blob(relative_path)
        blob.upload_from_string(content)
        return f"gs://{self.bucket_name}/{relative_path}"

    def read_bytes(self, relative_path: str) -> bytes:
        blob = self.bucket.blob(relative_path)
        if not blob.exists():
            raise StorageError(f"File not found in GCS: gs://{self.bucket_name}/{relative_path}")
        return blob.download_as_bytes()

    def exists(self, relative_path: str) -> bool:
        blob = self.bucket.blob(relative_path)
        return blob.exists()

    def list_files(self, relative_dir: str) -> list[str]:
        return sorted(blob.name for blob in self.client.list_blobs(self.bucket, prefix=relative_dir))
