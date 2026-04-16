# Airflow local runnable

This setup is designed for soutenance use: simple, local, and easy to show.

## What it provides

- one local Airflow instance in Docker
- the project DAG visible in the UI
- deterministic demo credentials
- direct execution of the existing project scripts from the DAG

## Prerequisites

- Docker Desktop installed and running
- the project root mounted locally

## Start Airflow

From the project root:

```bash
docker compose -f airflow/docker-compose.yml up --build
```

UI:

- URL: `http://127.0.0.1:8080`
- Username: `admin`
- Password: `admin`

## DAG to show

- DAG id: `energy_datalake_batch`
- Execution mode: manual trigger from the Airflow UI

Task order:

1. `init_db`
2. `transform`
3. `load`
4. `gold`
5. `manifest`
6. `atlas_export`
7. `monitoring`
8. `backup`

## Recommended soutenance flow

1. Open the DAG graph view.
2. Explain that the DAG orchestrates the same local scripts already used in the project.
3. Trigger one manual run.
4. Show that the DAG executes the full batch chain from reset to monitoring.
5. Go back to the repo artifacts:
   `prevision_energie.db`, `atlas/atlas_bundle.json`, `docs/datalake_manifest.json`.

## Stop Airflow

```bash
docker compose -f airflow/docker-compose.yml down
```

To also remove the persisted Airflow metadata volume:

```bash
docker compose -f airflow/docker-compose.yml down -v
```
