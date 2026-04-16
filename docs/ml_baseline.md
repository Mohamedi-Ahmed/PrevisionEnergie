# ML baseline - demonstration sobre et runnable

Cette brique ajoute une evaluation predictive legere au-dessus de `gold_daily_features`, sans changer l'architecture du projet.

## Positionnement

- dataset source : vrai fichier Kaggle `merged_daily_regional.csv`
- pipeline conserve : ingestion Bronze -> Silver -> Gold
- evaluation : baseline naive `lag_1` comparee a une regression lineaire simple
- split : temporel, avec la fin de serie reservee au test

## Commandes

### 1. Rejouer le pipeline depuis le vrai dataset Kaggle

```bash
python scripts/run_real_kaggle_pipeline.py
```

### 2. Calculer les metriques ML

```bash
python scripts/run_ml_baseline.py
```

## Artefacts produits

- `data/gold/exports/ml_metrics.json`
- `data/gold/exports/ml_predictions.csv`

## Metriques presentes

- `R2`
- `MAE`
- `RMSE`

## Lecture soutenance

Le bon discours n'est pas de pretendre a une plateforme MLOps complete. Le projet montre surtout :

- une base de donnees fiable ;
- un jeu de features quotidien coherent ;
- une comparaison simple entre baseline naive et modele lineaire ;
- des resultats chiffrables et reproductibles.
