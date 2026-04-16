# Soutenance - mode demo recommande

Ce guide privilegie un parcours simple, stable et coherent avec les livrables deja remis.

## Parcours le plus sur

### 1. Rejouer la preparation locale

```bash
python scripts/run_soutenance_demo.py
```

Ce script :
- reinitialise la base SQLite locale ;
- ingere le petit fichier Kaggle de demo ;
- enrichit la demo avec une API mock locale ;
- reconstruit Silver, Gold, le bundle Atlas et le manifeste Data Lake ;
- affiche un resume des preuves observables.

### 2. Ouvrir l'API

```bash
python scripts/run_api.py
```

Puis ouvrir :
- `http://127.0.0.1:8000/docs`

### 3. Authentification Swagger

1. Executer `POST /api/v1/auth/token`
2. Utiliser les credentials de `.env` ou les placeholders de `.env.example`
3. Copier le `access_token`
4. Cliquer sur `Authorize` dans Swagger et coller `Bearer <token>`

### 4. Requete API a montrer

Exemple stable :

```text
GET /api/v1/features?start_date=2013-01-01&end_date=2013-01-03&region=Auvergne-Rhone-Alpes
```

## Preuves a montrer pendant la demo

- E4 pipeline :
  `python scripts/run_soutenance_demo.py`
- Requete SQL :
  `sql/queries/feature_aggregations.sql`
- API :
  `/docs` puis `GET /api/v1/features`
- E5 Gold / DWH :
  `python scripts/run_gold.py`
- Gouvernance locale :
  `python scripts/run_governance_demo.py`
- Baseline ML :
  `python scripts/run_ml_baseline.py`

## Fichiers utiles a ouvrir a l'oral

- `app/api/routers/features.py`
- `sql/queries/feature_aggregations.sql`
- `sql/ddl/create_gold_tables.sql`
- `app/db/loaders/gold_loader.py`
- `airflow/dags/energy_datalake_batch.py`
- `app/governance/rbac.py`
- `app/governance/lifecycle.py`

## Fichiers a ne pas mettre au centre du walkthrough

- `scripts/build_soutenance_pptx.py`
- `scripts/generate_final_livrables_docx.py`
- `scripts/generate_final_livrables_pdf.py`

Ces scripts servent a generer les supports. Ils peuvent etre cites en fin de demo, mais ils ne doivent pas porter la preuve principale du niveau data engineer.

## Fallbacks plus surs

- Si Swagger pose probleme :
  montrer `tests/integration/test_api.py` puis relancer `python scripts/run_api.py`
- Si Airflow n'est pas pret :
  montrer le DAG dans `airflow/dags/energy_datalake_batch.py` et garder `docs/airflow_local.md` comme support
- Si on manque de temps :
  garder le trio `run_soutenance_demo.py` + `/docs` + `run_governance_demo.py`

## Scripts de synthese a garder en reserve

- `python scripts/run_dwh_demo.py`
- `python scripts/run_datalake_demo.py`

Ces scripts donnent un recap rapide des artefacts et des tables si on te demande une vue d'ensemble. Ils viennent apres le walkthrough principal.

## Checklist rapide avant passage

- La base `prevision_energie.db` existe
- `atlas/atlas_bundle.json` existe
- `docs/datalake_manifest.json` existe
- `data/gold/exports/ml_metrics.json` existe
- `python -m pytest tests/unit/test_run_soutenance_demo.py tests/integration/test_api.py tests/integration/test_scd2_dim_region.py -q`
