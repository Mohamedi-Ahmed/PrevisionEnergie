# E5 - DWH, DDL, Silver -> Gold, idempotence

Ce document couvre uniquement la partie E5 reellement implementee dans le code.

## Modele cible

Le Gold suit une logique Kimball :
- `dim_date`
- `dim_region`
- `dim_energy`
- `dim_weather_context`
- `fact_energy_consumption_daily`

Une table de service `gold_daily_features` reste exposee pour l'API et la demonstration.

## Grain retenu

- Fact table : 1 ligne par `jour x region x energie`
- Service table : 1 ligne par `jour x region`

Le loader force ce grain avant chargement pour eviter les doublons provenant de Silver.

## Fichiers a montrer

- Loader Gold : `app/db/loaders/gold_loader.py`
- DDL SQLite Gold : `sql/ddl/create_gold_tables.sql`
- DDL Delta cible : `sql/delta/create_gold_tables_delta.sql`
- MERGE Delta : `sql/delta/merge_gold_tables_delta.sql`

## Idempotence

En local SQLite :
- dimensions et fact charges par `INSERT ... ON CONFLICT DO UPDATE`
- `gold_daily_features` chargee par une logique de type `MERGE` avec table de stage temporaire

En cible Delta :
- scripts `MERGE INTO` fournis dans `sql/delta/merge_gold_tables_delta.sql`

## Commande de demo

```bash
python scripts/run_gold.py
```

Le script affiche un resume avec le nombre de lignes chargees dans les dimensions, la fact table et la table de service.
