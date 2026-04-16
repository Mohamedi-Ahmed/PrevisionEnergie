# E4 - Ingestion, SQL, ETL Bronze -> Silver, API

Ce document decrit uniquement le perimetre E4 tel qu'il est implemente dans le code.

## Ce qui est implemente

- Ingestion multi-source dans `app/ingestion/`
- Ecriture des fichiers bruts en Bronze via `StorageBackend`
- Journal d'ingestion SQLite `bronze_ingestion_log`
- Pipeline Bronze -> Silver dans `app/processing/pipeline.py`
- Validation des colonnes obligatoires (`date`, `region`)
- Nettoyage, normalisation, cast, dedoublonnage, imputation simple, clipping outliers, DJU
- Requetes SQL parametrees dans `sql/queries/`
- Endpoint FastAPI de lecture des features dans `app/api/routers/features.py`

## Ou regarder dans le code

- Ingestion Kaggle : `app/ingestion/kaggle_extractor.py`
- Ingestion API : `app/ingestion/api_base.py`
- Client HTTP avec retry : `app/ingestion/http_client.py`
- ETL Bronze -> Silver : `app/processing/pipeline.py`
- Requete SQL de features : `sql/queries/feature_aggregations.sql`
- Repository SQL parametre : `app/db/repositories/feature_repository.py`
- API FastAPI : `app/api/main.py`

## Commandes utiles

```bash
python scripts/init_db.py --reset
python scripts/run_pipeline.py
python scripts/run_api.py
python -m pytest tests/ -v
```

## Ce que montrent les tests E4

- `tests/integration/test_extractors.py` : ingestion Kaggle + alimentation du journal Bronze
- `tests/unit/test_api_ingestion.py` : ingestion API JSON + retry HTTP
- `tests/unit/test_bronze_to_silver_processor.py` : transformation Bronze -> Silver et validation de schema
- `tests/unit/test_feature_repository.py` : filtre region/date et protection par SQL parametre
- `tests/integration/test_api.py` : endpoint FastAPI `/api/v1/features`

## Limites assumees

- Le stockage est local par defaut pour garder une demo simple et runnable
- La base est SQLite pour la preuve technique et la soutenance
- L'API expose une couche de lecture simple, pas une plateforme complete de production
