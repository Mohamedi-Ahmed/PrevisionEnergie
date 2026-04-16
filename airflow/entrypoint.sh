#!/usr/bin/env bash
set -euo pipefail

export AIRFLOW_HOME="${AIRFLOW_HOME:-/opt/airflow}"

airflow db migrate

airflow users create \
  --username "${AIRFLOW_DEMO_USERNAME:-admin}" \
  --password "${AIRFLOW_DEMO_PASSWORD:-admin}" \
  --firstname Demo \
  --lastname User \
  --role Admin \
  --email demo@prevision-energie.local || true

airflow scheduler &
exec airflow webserver
