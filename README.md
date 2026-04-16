# PrevisionEnergie

Pipeline data sur la consommation d'électricité et de gaz par région en France, avec prévisions météo-énergie.

Sources : Kaggle (historique journalier), RTE, Open-Meteo. Stockage SQLite en local, architecture Bronze / Silver / Gold, API FastAPI, baseline ML + Random Forest, orchestration Airflow.

## Démarrer

```bash
python scripts/run_soutenance_demo.py
python scripts/run_api.py
```

Puis Swagger sur http://127.0.0.1:8000/docs.

Le premier script initialise SQLite, charge le CSV Kaggle de démo, enrichit via une API mock, et reconstruit Silver + Gold + le bundle Atlas. Le second lance l'API.

## Pipeline étape par étape

Si tu veux rejouer chaque maillon à la main :

```bash
python scripts/init_db.py
python scripts/run_transform.py --source kaggle
python scripts/run_load.py --source kaggle
python scripts/run_gold.py
python scripts/run_api.py
```

## Dataset Kaggle complet + ML

```bash
python scripts/run_real_kaggle_pipeline.py
python scripts/run_ml_baseline.py
python scripts/run_forecast.py
```

Les métriques et prédictions sortent dans `data/gold/exports/` (`ml_metrics.json`, `ml_predictions.csv`) et `data/ml/` pour le forecast Random Forest.

## Airflow

```bash
docker compose -f airflow/docker-compose.yml up --build
```

UI sur http://127.0.0.1:8080 (`admin` / `admin`). Le DAG `energy_datalake_batch` enchaîne init_db → transform → load → gold → manifest → atlas_export → monitoring → backup.

## Gouvernance & monitoring

```bash
python scripts/run_governance_demo.py
python scripts/run_monitoring.py
```

RBAC par zone (Bronze / Silver / Gold), SCD2 sur `dim_region`, politique de rétention, health checks (fraîcheur, volume, schéma) avec alertes JSONL.

## Tests

```bash
python -m pytest tests/ -v
```

## Arborescence

```text
app/          # ingestion, processing, db, api, governance, ml
sql/          # DDL, requêtes, vues, delta
airflow/      # Dockerfile + DAG
configs/      # YAML (datalake, monitoring)
atlas/        # bundle catalogue de données
scripts/      # CLI (ingestion, ETL, démo, génération livrables)
tests/        # unit + integration
docs/         # guides par bloc, référentiels, manifeste
```

## Stack

Python 3.11 · FastAPI · Pandas · Pydantic · SQLAlchemy · SQLite · pytest · Airflow · scikit-learn · Docker

## Auteur

Ahmed Mohamedi — [mohamedi.ahmed93@gmail.com](mailto:mohamedi.ahmed93@gmail.com)
