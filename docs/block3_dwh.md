# Bloc 3 - DWH Gold

Ce document décrit l’extension Bloc 3 ajoutée au projet :
- schéma en étoile ;
- dimensions : date, région, énergie, contexte météo ;
- fait : consommation journalière par région et énergie ;
- conservation de `gold_daily_features` comme table de restitution.

## Exécution

```bash
python scripts/init_db.py
python scripts/run_etl.py --source kaggle --build-gold
```

## Tables créées
- `dim_date`
- `dim_region`
- `dim_energy`
- `dim_weather_context`
- `fact_energy_consumption_daily`
- `gold_daily_features`

## Logique retenue
La couche Silver reste la couche d’intégration. La couche Gold devient la couche décisionnelle.
