# PrevisionEnergie - Pipeline de donnees

## Le projet

Projet de pipeline de donnees autour de la consommation energetique regionale en France.

Le projet contient :
- ingestion multi-sources ;
- pipeline Bronze -> Silver ;
- chargement SQL et couche Gold ;
- API FastAPI de consultation ;
- baseline ML legere avec metriques sur `gold_daily_features` ;
- scripts de gouvernance et de datalake utilises pendant la soutenance.

## Lancement rapide

```bash
python scripts/run_soutenance_demo.py
python scripts/run_api.py
```

API Swagger :
- `http://127.0.0.1:8000/docs`

Parcours soutenance :

```bash
python scripts/run_soutenance_demo.py
python scripts/run_api.py
python scripts/run_governance_demo.py
```

Guide pas a pas :
- `docs/soutenance_demo.md`

## Variante E4

```powershell
python scripts/run_pipeline.py `
  --kaggle-source-file data/bronze/kaggle/demo_pipeline.csv `
  --api-source rte `
  --api-absolute-url https://example.test/rte `
  --api-params "{}"
```

Commande de demo soutenance :

```bash
python scripts/run_soutenance_demo.py
```

## Variante Kaggle complet + baseline ML

```bash
python scripts/run_real_kaggle_pipeline.py
python scripts/run_ml_baseline.py
```

Artefacts produits :
- `data/gold/exports/ml_metrics.json`
- `data/gold/exports/ml_predictions.csv`

Exemple de resultat sur un run local du dataset Kaggle journalier :
- electricite : `R2 = 0.9882` pour la regression lineaire contre `0.9748` pour la baseline naive `lag_1`
- gaz : `R2 = 0.9655` pour la regression lineaire contre `0.9526` pour la baseline naive `lag_1`

## Etapes principales

```bash
python scripts/init_db.py
python scripts/run_transform.py --source kaggle
python scripts/run_load.py --source kaggle
python scripts/run_gold.py
python scripts/run_api.py
```

## Tests

```bash
python -m pytest tests/ -v
```

## Documentation utile

- Guide soutenance : `docs/soutenance_demo.md`
- Guide E4 : `docs/e4_guide.md`
- Baseline ML : `docs/ml_baseline.md`
- Airflow local : `docs/airflow_local.md`
- Manifest datalake : `docs/datalake_manifest.json`

## Coeur du walkthrough code

- Ingestion : `app/ingestion/`
- Bronze -> Silver : `app/processing/pipeline.py`
- Gold / chargement SQL : `app/db/loaders/gold_loader.py` et `sql/`
- API FastAPI : `app/api/`
- Gouvernance locale : `app/governance/`

## Airflow local

Section optionnelle pour la soutenance.

```bash
docker compose -f airflow/docker-compose.yml up --build
```

- UI : `http://127.0.0.1:8080`
- Login : `admin`
- Mot de passe : `admin`
- DAG : `energy_datalake_batch`

## Structure

```text
app/
|-- api/
|-- core/
|-- db/
|-- etl/
|-- governance/
|-- ingestion/
|-- processing/
|-- storage/
`-- utils/
sql/
configs/
atlas/
airflow/
tests/
docs/
```

## Stack

Python 3.11, FastAPI, Pandas, SQLite, Pydantic, pytest, Airflow
