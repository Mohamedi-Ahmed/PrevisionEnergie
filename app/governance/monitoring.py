"""
Monitoring et alerting pour le pipeline PrevisionEnergie.

Ce module implémente :
- La journalisation catégorisée (INFO, WARNING, ERROR, CRITICAL)
- Les health checks (base, fraîcheur, volumétrie)
- La génération d'alertes lors de ruptures de service
- Le suivi des indicateurs SLA

Compétences couvertes : C16 (alertes, journalisation) et C20 (monitorage, alertes sur rupture).
"""

from __future__ import annotations

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import yaml

from app.core.config import BASE_DIR, get_settings

logger = logging.getLogger("prevision_energie.monitoring")

MONITORING_CONFIG_PATH = BASE_DIR / "configs" / "monitoring.yaml"
ALERT_LOG_PATH = BASE_DIR / "data" / "monitoring" / "alerts.jsonl"


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

def _load_monitoring_config() -> dict[str, Any]:
    if MONITORING_CONFIG_PATH.exists():
        with MONITORING_CONFIG_PATH.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def get_sla_config() -> dict[str, Any]:
    return _load_monitoring_config().get("sla", {})


def get_alert_config() -> dict[str, Any]:
    return _load_monitoring_config().get("alerts", {})


# ──────────────────────────────────────────────
# Journalisation catégorisée des alertes
# ──────────────────────────────────────────────

def _persist_alert(alert: dict[str, Any]) -> None:
    """Persiste une alerte dans le fichier JSONL pour traçabilité."""
    ALERT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ALERT_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(alert, ensure_ascii=False, default=str) + "\n")


def emit_alert(
    category: str,
    severity: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Émet une alerte catégorisée et la journalise.

    Categories : FRESHNESS, VOLUME, DATABASE, API_HEALTH, PIPELINE, BACKUP
    Severities : INFO, WARNING, ERROR, CRITICAL
    """
    alert = {
        "timestamp": datetime.utcnow().isoformat(),
        "category": category,
        "severity": severity,
        "message": message,
        "details": details or {},
    }

    log_level = getattr(logging, severity, logging.WARNING)
    logger.log(log_level, "[%s] %s — %s", severity, category, message)

    _persist_alert(alert)
    return alert


# ──────────────────────────────────────────────
# Health checks
# ──────────────────────────────────────────────

def check_database_health(db_path: Path | None = None) -> dict[str, Any]:
    """
    Vérifie que la base SQLite est accessible et non corrompue.
    Génère une alerte CRITICAL en cas de rupture de service.
    """
    if db_path is None:
        db_path = BASE_DIR / "prevision_energie.db"

    result = {"check": "database", "status": "ok", "path": str(db_path)}

    if not db_path.exists():
        alert = emit_alert(
            category="DATABASE",
            severity="CRITICAL",
            message=f"Base de données introuvable : {db_path}",
            details={"path": str(db_path)},
        )
        result["status"] = "critical"
        result["alert"] = alert
        return result

    try:
        conn = sqlite3.connect(db_path)
        conn.execute("SELECT 1")
        conn.close()
    except Exception as exc:
        alert = emit_alert(
            category="DATABASE",
            severity="CRITICAL",
            message=f"Base de données inaccessible : {exc}",
            details={"path": str(db_path), "error": str(exc)},
        )
        result["status"] = "critical"
        result["alert"] = alert
        return result

    emit_alert(
        category="DATABASE",
        severity="INFO",
        message="Base de données accessible",
        details={"path": str(db_path)},
    )
    return result


def check_data_freshness(db_path: Path | None = None) -> dict[str, Any]:
    """
    Vérifie la fraîcheur des données Silver (dernier inserted_at).
    Génère une alerte WARNING si les données dépassent le seuil SLA.
    """
    if db_path is None:
        db_path = BASE_DIR / "prevision_energie.db"

    sla = get_sla_config()
    max_hours = sla.get("data_freshness_max_hours", 48)

    result = {"check": "freshness", "status": "ok", "max_hours": max_hours}

    if not db_path.exists():
        result["status"] = "skipped"
        result["reason"] = "database not found"
        return result

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT MAX(inserted_at) FROM silver_energy_weather_daily"
        )
        row = cursor.fetchone()
        conn.close()
    except Exception:
        result["status"] = "skipped"
        result["reason"] = "table not found or query failed"
        return result

    if row is None or row[0] is None:
        alert = emit_alert(
            category="FRESHNESS",
            severity="WARNING",
            message="Aucune donnée Silver trouvée",
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
            message=f"Données Silver périmées ({age_hours:.0f}h > seuil {max_hours}h)",
            details={"last_load": last_load.isoformat(), "age_hours": age_hours},
        )
        result["status"] = "warning"
        result["alert"] = alert
    else:
        emit_alert(
            category="FRESHNESS",
            severity="INFO",
            message=f"Fraîcheur OK ({age_hours:.0f}h)",
        )

    return result


def check_data_volume(db_path: Path | None = None) -> dict[str, Any]:
    """
    Vérifie la volumétrie Gold (nombre de lignes dans fact_energy_consumption_daily).
    Génère une alerte ERROR si en dessous du seuil SLA.
    """
    if db_path is None:
        db_path = BASE_DIR / "prevision_energie.db"

    sla = get_sla_config()
    min_rows = sla.get("gold_min_row_count", 100)

    result = {"check": "volume", "status": "ok", "min_rows": min_rows}

    if not db_path.exists():
        result["status"] = "skipped"
        return result

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute(
            "SELECT COUNT(*) FROM fact_energy_consumption_daily"
        )
        count = cursor.fetchone()[0]
        conn.close()
    except Exception:
        result["status"] = "skipped"
        result["reason"] = "table not found"
        return result

    result["row_count"] = count
    if count < min_rows:
        alert = emit_alert(
            category="VOLUME",
            severity="ERROR",
            message=f"Volumétrie Gold insuffisante ({count} < {min_rows})",
            details={"row_count": count, "threshold": min_rows},
        )
        result["status"] = "error"
        result["alert"] = alert
    else:
        emit_alert(
            category="VOLUME",
            severity="INFO",
            message=f"Volumétrie Gold OK ({count} lignes)",
        )

    return result


# ──────────────────────────────────────────────
# Rapport de monitoring complet
# ──────────────────────────────────────────────

def run_all_checks(db_path: Path | None = None) -> dict[str, Any]:
    """
    Exécute tous les health checks et retourne un rapport consolidé.
    Utilisé par le endpoint /monitoring et par le script de monitoring.
    """
    checks = [
        check_database_health(db_path),
        check_data_freshness(db_path),
        check_data_volume(db_path),
    ]

    overall = "ok"
    for check in checks:
        if check["status"] == "critical":
            overall = "critical"
            break
        if check["status"] == "error" and overall != "critical":
            overall = "error"
        if check["status"] == "warning" and overall in ("ok",):
            overall = "warning"

    report = {
        "timestamp": datetime.utcnow().isoformat(),
        "overall_status": overall,
        "sla": get_sla_config(),
        "checks": checks,
    }

    logger.info("Monitoring report: overall=%s", overall)
    return report
