# Mapping Bloc 3 - Référentiel / dépôt

Ce document aligne les attendus du Bloc 3 avec les éléments présents dans le dépôt.

| Compétence | Attendu | Élément du dépôt |
|---|---|---|
| C13 | Schéma en étoile Kimball | `sql/ddl/create_gold_tables.sql`, `app/db/loaders/gold_loader.py`, `docs/block3_dwh.md` |
| C14 | Création du DWH | `sql/ddl/create_gold_tables.sql`, `sql/delta/create_gold_tables_delta.sql`, `scripts/run_gold.py` |
| C15 | ETL Silver -> Gold | `app/db/loaders/gold_loader.py`, `scripts/run_etl.py --build-gold`, `app/etl/orchestrator.py` |
| C16 | Catalogue et lignage | `atlas/`, `scripts/export_atlas_metadata.py`, `docs/block3_governance.md` |
| C17 | SCD Type 2 | `dim_region`, `app/db/loaders/gold_loader.py`, `sql/queries/dim_region_history.sql` |

## Lecture recommandée pour le jury
1. `README.md`
2. `docs/block3_dwh.md`
3. `docs/block3_governance.md`
4. `docs/bloc3_referential_mapping.md`
