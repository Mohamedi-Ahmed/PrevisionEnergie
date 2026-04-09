# PrevisionEnergie — Pipeline Data Engineer (Bloc 2 / 3 / 4)

## Le projet
Pipeline de données pour la prévision de consommation énergétique régionale en France.

Ce dépôt couvre :
- ingestion multi-sources (Kaggle, API RTE, Météo-France, data.gouv.fr) ;
- pipeline Bronze → Silver (nettoyage, normalisation, DJU, quality reports) ;
- entrepôt de données Gold en schéma en étoile Kimball ;
- API REST FastAPI avec authentification Bearer ;
- gouvernance Data Lake (RBAC, rétention, catalogue Atlas).

## Lancement

```bash
# Tout-en-un : initialise la base, transforme, charge, construit le Gold
python scripts/run_demo_setup.py

# Lancer l'API
python scripts/run_api.py
# -> http://127.0.0.1:8000/docs
```

## Étape par étape

```bash
python scripts/init_db.py                        # Schéma SQLite
python scripts/run_transform.py --source kaggle  # Bronze → Silver
python scripts/run_load.py --source kaggle       # Silver → SQL
python scripts/run_gold.py                       # Silver → Gold DWH
python scripts/run_api.py                        # API FastAPI
```

## Tests

```bash
python -m pytest tests/ -v
```

21 tests (unit + intégration).

## API

FastAPI avec documentation OpenAPI auto-générée sur `/docs`.
Identifiants par défaut dans `.env.example`, surchargeables via `.env`.

## Bloc 2 — Collecte, stockage, mise à disposition

- 4 extracteurs : `app/ingestion/` (Kaggle, RTE, Météo-France, data.gouv)
- Pipeline Bronze → Silver : `app/processing/pipeline.py`
- Requêtes SQL paramétrées : `sql/queries/`
- API REST : `app/api/`

## Bloc 3 — Entrepôt de données

- Schéma en étoile : 1 fait (`fact_energy_consumption_daily`) + 4 dimensions (date, région, énergie, contexte météo)
- SCD Type 2 sur `dim_region` (valid_from / valid_to, hash MD5)
- Chargement idempotent via MERGE upsert
- Catalogue Atlas : `atlas/`
- DDL cible Delta Lake : `sql/delta/create_gold_tables_delta.sql`

```bash
python scripts/run_gold.py
python scripts/export_atlas_metadata.py
```

## Bloc 4 — Data Lake et gouvernance

Le Bloc 4 formalise l'architecture Medallion existante :
- Bronze → zone Raw
- Silver → zone Curated
- Gold → zone Consumption

Ajouts :
- RBAC 3 rôles : `app/governance/rbac.py`
- Politique de rétention par zone : `app/governance/lifecycle.py`
- DAG Airflow : `airflow/dags/energy_datalake_batch.py`
- Manifeste Data Lake : `docs/datalake_manifest.json`

```bash
python scripts/generate_datalake_manifest.py
python scripts/run_bloc4_demo.py
```

## Structure du projet

```
app/
├── api/          # FastAPI (routers, schemas, auth)
├── core/         # Config, logging, sécurité
├── db/           # Connexion SQLite, loaders, repositories
├── etl/          # Orchestration pipeline
├── governance/   # RBAC, lifecycle
├── ingestion/    # Extracteurs multi-sources
├── processing/   # Bronze → Silver (cleaners, DJU, outliers, quality)
├── storage/      # Abstraction StorageBackend (local / GCS)
└── utils/
sql/              # DDL, DML, requêtes, vues
configs/          # YAML (settings, datalake, sources)
atlas/            # Metadata catalogue Apache Atlas
airflow/          # DAG batch
tests/            # Unit + intégration
docs/             # Architecture, API contract, data dictionary
```

## Stack

Python 3.11 · FastAPI · Pandas · SQLite · Pydantic · pytest · Airflow (DAG)
