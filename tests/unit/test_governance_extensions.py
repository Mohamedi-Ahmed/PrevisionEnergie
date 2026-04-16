from datetime import date
import json
import sqlite3

from app.governance.lifecycle import get_expiration_date, should_expire
from app.governance.monitoring import check_data_volume, check_metadata_assets
from app.governance.rbac import get_zone_access_matrix
from scripts.export_atlas_metadata import build_bundle, summarize_bundle


def test_get_expiration_date_is_exact() -> None:
    assert get_expiration_date("consumption", date(2023, 6, 15)) == date(2025, 6, 15)


def test_should_expire_uses_exact_cutoff() -> None:
    assert should_expire("consumption", date(2023, 6, 15), date(2025, 6, 14)) is False
    assert should_expire("consumption", date(2023, 6, 15), date(2025, 6, 15)) is True


def test_zone_access_matrix_reads_yaml() -> None:
    matrix = get_zone_access_matrix()
    assert matrix["raw"]["owner_role"] == "data_engineer"
    assert "data_reader" in matrix["consumption"]["reader_roles"]


def test_atlas_bundle_summary_has_expected_sections() -> None:
    bundle = build_bundle()
    summary = summarize_bundle(bundle)
    assert summary["files"] >= 5
    assert summary["entity_files"] >= 2
    assert summary["glossary_files"] == 1


def test_metadata_assets_check_ok(tmp_path, monkeypatch) -> None:
    atlas_dir = tmp_path / "atlas"
    docs_dir = tmp_path / "docs"
    atlas_dir.mkdir()
    docs_dir.mkdir()
    (atlas_dir / "atlas_bundle.json").write_text(json.dumps({"ok": True}), encoding="utf-8")
    (docs_dir / "datalake_manifest.json").write_text(json.dumps({"ok": True}), encoding="utf-8")

    from app.governance import monitoring as monitoring_module

    monkeypatch.setattr(monitoring_module, "BASE_DIR", tmp_path)
    result = check_metadata_assets()
    assert result["status"] == "ok"


def test_check_data_volume_accepts_demo_threshold_override(tmp_path) -> None:
    db_path = tmp_path / "demo.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE fact_energy_consumption_daily (
                fact_id INTEGER PRIMARY KEY,
                consumption_value REAL
            )
            """
        )
        connection.executemany(
            "INSERT INTO fact_energy_consumption_daily (consumption_value) VALUES (?)",
            [(1.0,), (2.0,), (3.0,), (4.0,)],
        )
        connection.commit()

    result = check_data_volume(db_path, min_rows_override=1)
    assert result["status"] == "ok"
    assert result["row_count"] == 4
    assert result["min_rows"] == 1
