import pytest

from app.core.config import get_settings
from app.db.sql_runner import SQLRunner
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


def test_kaggle_extractor_persists_bronze_log(tmp_path, monkeypatch):
    """Une ingestion reussie alimente le journal Bronze dans SQLite."""
    db_path = tmp_path / "extractors.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    get_settings.cache_clear()

    runner = SQLRunner()
    runner.run_directory("sql/ddl")

    source_file = tmp_path / "sample.csv"
    source_file.write_text(
        "date,region,electricity_consumption\n2024-01-01,ile de france,100\n",
        encoding="utf-8",
    )

    storage = LocalStorageBackend(base_path=str(tmp_path / "data"))
    extractor = KaggleExtractor(storage_backend=storage)
    result = extractor.extract(source_file_path=str(source_file))

    import sqlite3

    connection = sqlite3.connect(db_path)
    row = connection.execute(
        """
        SELECT source_name, storage_path, row_count, load_status
        FROM bronze_ingestion_log
        """
    ).fetchone()
    connection.close()

    assert result.record_count == 1
    assert row == ("kaggle", result.storage_path, 1, "INGESTED")

    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()
