import sqlite3

import httpx
import pytest

from app.core.config import get_settings
from app.db.sql_runner import SQLRunner
from app.ingestion.api_base import BaseAPIExtractor
from app.ingestion.http_client import HTTPIngestionClient
from app.storage.local import LocalStorageBackend


class DummyAPIExtractor(BaseAPIExtractor):
    source_name = "dummy_api"

    def __init__(self, storage_backend) -> None:
        super().__init__(storage_backend=storage_backend, bronze_subdir="bronze/dummy_api")


@pytest.fixture()
def ingestion_db(tmp_path, monkeypatch):
    db_path = tmp_path / "api_ingestion.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    get_settings.cache_clear()
    SQLRunner().run_directory("sql/ddl")
    yield db_path
    monkeypatch.delenv("DATABASE_URL", raising=False)
    get_settings.cache_clear()


def test_api_extractor_persists_json_payload_and_bronze_log(tmp_path, ingestion_db) -> None:
    storage = LocalStorageBackend(base_path=str(tmp_path / "data"))
    extractor = DummyAPIExtractor(storage_backend=storage)
    extractor.client.get_json = lambda **kwargs: [{"region": "idf"}, {"region": "occitanie"}]

    result = extractor.extract(endpoint="/demo", destination_filename="demo.json")

    assert result.record_count == 2
    assert storage.exists(result.storage_path)

    with sqlite3.connect(ingestion_db) as connection:
        row = connection.execute(
            """
            SELECT source_name, storage_path, row_count, load_status
            FROM bronze_ingestion_log
            """
        ).fetchone()

    assert row == ("dummy_api", result.storage_path, 2, "INGESTED")


def test_http_ingestion_client_retries_before_success(monkeypatch) -> None:
    attempts = {"count": 0}

    class DummyResponse:
        def __init__(self) -> None:
            self.content = b'{"status": "ok"}'

        def raise_for_status(self) -> None:
            return None

        def json(self):
            return {"status": "ok"}

    def fake_get(url, params=None, headers=None, timeout=None):
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise httpx.ConnectError("temporary failure")
        return DummyResponse()

    monkeypatch.setattr(httpx, "get", fake_get)

    client = HTTPIngestionClient(max_retries=2, backoff_seconds=0.0)
    payload = client.get_json(absolute_url="https://example.test/demo")

    assert payload == {"status": "ok"}
    assert attempts["count"] == 3
