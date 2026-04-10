"""
Script de monitoring — exécute tous les health checks et affiche le rapport.

Usage :
    python scripts/run_monitoring.py

Intégrable dans un cron ou dans le DAG Airflow comme tâche de contrôle.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from app.core.logger import setup_logging
from app.governance.monitoring import run_all_checks

setup_logging()


def main() -> None:
    report = run_all_checks()
    print(json.dumps(report, indent=2, ensure_ascii=False, default=str))

    if report["overall_status"] == "critical":
        print("\n*** ALERTE CRITIQUE : rupture de service détectée ***")
        sys.exit(2)
    elif report["overall_status"] == "error":
        print("\n*** ALERTE : anomalie détectée ***")
        sys.exit(1)
    else:
        print("\n✓ Tous les checks sont passés")
        sys.exit(0)


if __name__ == "__main__":
    main()
