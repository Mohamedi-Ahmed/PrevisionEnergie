from __future__ import annotations

import os
from pathlib import Path
import sys

try:
    from airflow import DAG
    from airflow.operators.bash import BashOperator
except ImportError:  # pragma: no cover
    DAG = None
    BashOperator = None


PROJECT_DIR = Path(
    os.getenv(
        "PREVISION_ENERGIE_PROJECT_DIR",
        Path(__file__).resolve().parents[2],
    )
)


def command(script: str) -> str:
    python = sys.executable
    return f'cd "{PROJECT_DIR}" && {python} {script}'


if DAG is not None:
    from datetime import datetime

    with DAG(
        dag_id="energy_datalake_batch",
        start_date=datetime(2025, 1, 1),
        schedule=None,
        catchup=False,
        tags=["bloc4", "datalake", "energy"],
        description="Orchestration batch locale de demonstration pour le Data Lake energie et meteo.",
    ) as dag:
        init_db = BashOperator(task_id="init_db", bash_command=command("scripts/init_db.py --reset"))
        transform = BashOperator(task_id="transform", bash_command=command("scripts/run_transform.py --source kaggle"))
        load = BashOperator(task_id="load", bash_command=command("scripts/run_load.py --source kaggle"))
        gold = BashOperator(task_id="gold", bash_command=command("scripts/run_gold.py"))
        manifest = BashOperator(task_id="manifest", bash_command=command("scripts/generate_datalake_manifest.py"))
        atlas = BashOperator(task_id="atlas_export", bash_command=command("scripts/export_atlas_metadata.py"))
        monitoring = BashOperator(task_id="monitoring", bash_command=command("scripts/run_monitoring.py"))
        backup = BashOperator(task_id="backup", bash_command=command("scripts/backup_db.py"))

        init_db >> transform >> load >> gold >> manifest >> atlas >> monitoring >> backup
