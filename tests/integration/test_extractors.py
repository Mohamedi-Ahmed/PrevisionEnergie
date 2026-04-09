import pytest

from app.storage.local import LocalStorageBackend
from app.ingestion.kaggle_extractor import KaggleExtractor


@pytest.fixture()
def local_backend(tmp_path):
    return LocalStorageBackend(base_path=str(tmp_path))


def test_kaggle_extractor_init(local_backend):
    """Le KaggleExtractor s'initialise sans erreur."""
    extractor = KaggleExtractor(storage_backend=local_backend)
    assert extractor is not None


def test_storage_backend_write_and_read(local_backend):
    """Ecriture puis relecture via le StorageBackend local."""
    content = b"date,region,value\n2024-01-01,idf,100"
    local_backend.write_bytes("bronze/test/sample.csv", content)
    assert local_backend.exists("bronze/test/sample.csv")
    read_back = local_backend.read_bytes("bronze/test/sample.csv")
    assert read_back == content


def test_storage_backend_list_files(local_backend):
    """List_files retourne les fichiers ecrits."""
    local_backend.write_bytes("bronze/test/a.csv", b"data")
    local_backend.write_bytes("bronze/test/b.csv", b"data")
    files = local_backend.list_files("bronze/test")
    assert len(files) >= 2
