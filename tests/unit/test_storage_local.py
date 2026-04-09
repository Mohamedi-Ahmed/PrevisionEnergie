from app.storage.local import LocalStorageBackend


def test_local_storage_write_read_exists(tmp_path) -> None:
    storage = LocalStorageBackend(base_path=str(tmp_path))
    storage.write_bytes("bronze/test/file.txt", b"hello")

    assert storage.exists("bronze/test/file.txt") is True
    assert storage.read_bytes("bronze/test/file.txt") == b"hello"
