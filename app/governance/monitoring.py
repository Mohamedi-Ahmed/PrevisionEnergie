"""Local monitoring helpers used by the demo and governance scripts."""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

from app.core.config import BASE_DIR
from app.db.connection import get_sqlite_database_path

logger = logging.getLogger("prevision_energie.monitoring")

MONITORING_CONFIG_PATH = BASE_DIR / "configs" / "monitoring.yaml"
ALERT_LOG_PATH = BASE_DIR / "data" / "monitoring" / "alerts.jsonl"


def _load_monitoring_config() -> dict[str, Any]:
    if MONITORING_CONFIG_PATH.exists():
        with MONITORING_CONFIG_PATH.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    return {}


def get_sla_config() -> dict[str, Any]:
    return _load_monitoring_config().get("sla", {})


def get_alert_config() -> dict[str, Any]:
    return _load_monitoring_config().get("alerts", {})


def _persist_alert(alert: dict[str, Any]) -> None:
    """Append alerts to a JSONL file so the demo keeps a simple trace."""
    ALERT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ALERT_LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(alert, ensure_ascii=False, default=str) + "\n")


def emit_alert(
    category: str,
    severity: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create, log, and persist one monitoring alert."""
    alert = {
        "timestamp": datetime.utcnow().isoformat(),
        "category": category,
        "severity": severity,
        "message": message,
        "details": details or {},
    }

    log_level = getattr(logging, severity, logging.WARNING)
    logger.log(log_level, "[%s] %s - %s", severity, category, message)

    _persist_alert(alert)
    return alert


def check_database_health(db_path: Path | None = None) -> dict[str, Any]:
    """Check that the SQLite database exists and answers a simple query."""
    if db_path is None:
        db_path = get_sqlite_database_path()

    result = {"check": "database", "status": "ok", "path": str(db_path)}

    if not db_path.exists():
        alert = emit_alert(
            category="DATABASE",
            severity="CRITICAL",
            message=f"Database file not found: {db_path}",
            details={"path": str(db_path)},
        )
        result["status"] = "critical"
        result["alert"] = alert
        return result

    try:
        connection = sqlite3.connect(db_path)
        connection.execute("SELECT 1")
        connection.close()
    except Exception as exc:
        alert = emit_alert(
            category="DATABASE",
            severity="CRITICAL",
            message=f"Database check failed: {exc}",
            details={"path": str(db_path), "error": str(exc)},
        )
        result["status"] = "critical"
        result["alert"] = alert
        return result

    emit_alert(
        category="DATABASE",
        severity="INFO",
        message="Database reachable",
        details={"path": str(db_path)},
    )
    return result


def check_data_freshness(db_path: Path | None = None) -> dict[str, Any]:
    """Check the latest Silver timestamp against the freshness threshold."""
    if db_path is None:
        db_path = get_sqlite_database_path()

    sla = get_sla_config()
    max_hours = sla.get("data_freshness_max_hours", 48)

    result = {"check": "freshness", "status": "ok", "max_hours": max_hours}

    if not db_path.exists():
        result["status"] = "skipped"
        result["reason"] = "database not found"
        return result

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.execute(
            "SELECT MAX(inserted_at) FROM silver_energy_weather_daily"
        )
        row = cursor.fetchone()
        connection.close()
    except Exception:
        result["status"] = "skipped"
        result["reason"] = "table not found or query failed"
        return result

    if row is None or row[0] is None:
        alert = emit_alert(
            category="FRESHNESS",
            severity="WARNING",
            message="No Silver data found",
        )
        result["status"] = "warning"
        result["alert"] = alert
        return result

    last_load = datetime.fromisoformat(row[0])
    age_hours = (datetime.utcnow() - last_load).total_seconds() / 3600
    result["last_load"] = last_load.isoformat()
    result["age_hours"] = round(age_hours, 1)

    if age_hours > max_hours:
        alert = emit_alert(
            category="FRESHNESS",
            severity="WARNING",
            message=f"Silver data too old ({age_hours:.0f}h > {max_hours}h)",
            details={"last_load": last_load.isoformat(), "age_hours": age_hours},
        )
        result["status"] = "warning"
        result["alert"] = alert
    else:
        emit_alert(
            category="FRESHNESS",
            severity="INFO",
            message=f"Freshness OK ({age_hours:.0f}h)",
        )

    return result


def check_data_volume(
    db_path: Path | None = None,
    min_rows_override: int | None = None,
) -> dict[str, Any]:
    """Check that the Gold fact table has enough rows for the current context."""
    if db_path is None:
        db_path = get_sqlite_database_path()

    sla = get_sla_config()
    min_rows = (
        min_rows_override
        if min_rows_override is not None
        else sla.get("gold_min_row_count", 100)
    )

    result = {"check": "volume", "status": "ok", "min_rows": min_rows}

    if not db_path.exists():
        result["status"] = "skipped"
        return result

    try:
        connection = sqlite3.connect(db_path)
        cursor = connection.execute("SELECT COUNT(*) FROM fact_energy_consumption_daily")
        count = cursor.fetchone()[0]
        connection.close()
    except Exception:
        result["status"] = "skipped"
        result["reason"] = "table not found"
        return result

    result["row_count"] = count
    if count < min_rows:
        alert = emit_alert(
            category="VOLUME",
            severity="ERROR",
            message=f"Gold volume below threshold ({count} < {min_rows})",
            details={"row_count": count, "threshold": min_rows},
        )
        result["status"] = "error"
        result["alert"] = alert
    else:
        emit_alert(
            category="VOLUME",
            severity="INFO",
            message=f"Gold volume OK ({count} rows)",
        )

    return result


def check_metadata_assets() -> dict[str, Any]:
    """Check that the local Atlas bundle and manifest were generated."""
    atlas_bundle = BASE_DIR / "atlas" / "atlas_bundle.json"
    manifest = BASE_DIR / "docs" / "datalake_manifest.json"

    result = {
        "check": "metadata_assets",
        "status": "ok",
        "atlas_bundle_exists": atlas_bundle.exists(),
        "manifest_exists": manifest.exists(),
    }
    if not atlas_bundle.exists() or not manifest.exists():
        missing = []
        if not atlas_bundle.exists():
            missing.append("atlas_bundle.json")
        if not manifest.exists():
            missing.append("datalake_manifest.json")
        alert = emit_alert(
            category="PIPELINE",
            severity="WARNING",
            message=f"Metadata assets missing: {', '.join(missing)}",
            details={"missing": missing},
        )
        result["status"] = "warning"
        result["alert"] = alert
        return result

    emit_alert(
        category="PIPELINE",
        severity="INFO",
        message="Metadata assets available",
        details={"atlas_bundle": str(atlas_bundle), "manifest": str(manifest)},
    )
    return result


def run_all_checks(
    db_path: Path | None = None,
    min_rows_override: int | None = None,
) -> dict[str, Any]:
    """Run all checks and return one consolidated monitoring report."""
    checks = [
        check_database_health(db_path),
        check_data_freshness(db_path),
        check_data_volume(db_path, min_rows_override=min_rows_override),
        check_metadata_assets(),
    ]

    overall = "ok"
    for check in checks:
        if check["status"] == "critical":
            overall = "critical"
            break
        if check["status"] == "error" and overall != "critical":
            overall = "error"
        if check["status"] == "warning" and overall == "ok":
            overall = "warning"

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": overall,
        "sla": get_sla_config(),
        "checks": checks,
    }

    logger.info("Monitoring report: overall=%s", overall)
    return report
