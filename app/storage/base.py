from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    """Abstract storage backend used by ingestion and ETL layers."""

    @abstractmethod
    def write_bytes(self, relative_path: str, content: bytes) -> Path | str:
        raise NotImplementedError

    @abstractmethod
    def read_bytes(self, relative_path: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def exists(self, relative_path: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_files(self, relative_dir: str) -> list[str]:
        raise NotImplementedError

    def write_text(self, relative_path: str, content: str, encoding: str = "utf-8") -> Path | str:
        return self.write_bytes(relative_path=relative_path, content=content.encode(encoding))

    def read_text(self, relative_path: str, encoding: str = "utf-8") -> str:
        return self.read_bytes(relative_path=relative_path).decode(encoding)
