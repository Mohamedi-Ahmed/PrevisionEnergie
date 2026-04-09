from pathlib import Path

from app.storage.base import StorageBackend


class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: str) -> None:
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def write_bytes(self, relative_path: str, content: bytes) -> Path:
        target = self.base_path / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return target

    def read_bytes(self, relative_path: str) -> bytes:
        target = self.base_path / relative_path
        return target.read_bytes()

    def exists(self, relative_path: str) -> bool:
        return (self.base_path / relative_path).exists()

    def list_files(self, relative_dir: str) -> list[str]:
        target_dir = self.base_path / relative_dir
        if not target_dir.exists():
            return []
        return sorted(
            str(path.relative_to(self.base_path))
            for path in target_dir.rglob("*")
            if path.is_file()
        )
