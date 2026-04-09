# Bloc 2 / Bloc 3 / Bloc 4 — Projet final Data Engineer

## Résumé
Ce dépôt implémente le socle technique du projet ainsi que les extensions Bloc 3 et Bloc 4 :
- ingestion multi-sources ;
- pipeline Bronze → Silver ;
- enrichissement optionnel de Kaggle par APIs ;
- chargement Silver → SQL ;
- requêtes SQL et API FastAPI ;
- mise en place d’un mini entrepôt de données Gold en schéma en étoile ;
- conservation d’un dataset Gold de restitution compatible avec l’existant ;
- formalisation de l’architecture Data Lake et de la gouvernance associée.

## Préparation rapide pour la soutenance
La commande la plus simple pour préparer une base locale démontrable avec les données d’exemple du dépôt est :

```bash
python scripts/run_demo_setup.py
```

Cette commande :
- initialise la base SQLite ;
- rejoue la transformation Bronze → Silver sur les fichiers d’exemple ;
- charge la Silver dans SQL ;
- construit la couche Gold DWH ;
- génère le bundle Atlas et le manifeste Data Lake.

## Lancement rapide détaillé
```bash
python scripts/init_db.py
python scripts/run_transform.py --source kaggle
python scripts/run_load.py --source kaggle
python scripts/run_gold.py
python scripts/run_api.py
```

## API
Le projet expose une API FastAPI documentée automatiquement.
Pour la démo locale, les identifiants par défaut sont définis dans `.env.example` et peuvent être surchargés dans `.env`.

## Ce que fait désormais le Bloc 3
Le projet conserve la logique du Bloc 2 mais ajoute une vraie couche DWH Gold :
- dimensions : date, région, énergie, contexte météo ;
- fait : consommation journalière par région et par énergie ;
- chargement incrémental idempotent côté SQLite via upsert ;
- préparation d’un positionnement Delta Lake dans la documentation et les scripts SQL dédiés.

## Compatibilité avec l’existant
La table `gold_daily_features` est conservée comme table de restitution / service dataset.
Elle peut continuer à alimenter l’API ou des usages analytiques simples, tandis que le schéma en étoile sert de socle DWH.

## Bloc 3 - E5 / E6
Le dépôt est désormais harmonisé avec les attendus du Bloc 3 :
- E5 : modélisation Kimball, tables Gold, loader Silver -> Gold, DDL cible Delta Lake ;
- E6 : préparation du catalogue Atlas, lignage bout en bout, logique SCD2 sur `dim_region`.

## Commandes utiles Bloc 3
```bash
python scripts/run_gold.py
python scripts/export_atlas_metadata.py
python scripts/run_bloc3_demo.py
```

## Fichiers repères
- `docs/block3_dwh.md`
- `docs/block3_governance.md`
- `docs/bloc3_referential_mapping.md`

## Ce que fait désormais le Bloc 4
Le Bloc 4 prolonge l’architecture Medallion existante sans la casser :
- Bronze est formalisé en zone Raw ;
- Silver est formalisé en zone Curated ;
- Gold est formalisé en zone Consumption ;
- une politique de rétention et un RBAC simple sont ajoutés ;
- un manifeste Data Lake et un DAG Airflow-ready sont fournis pour illustrer l’industrialisation progressive.

## Commandes utiles Bloc 4
```bash
python scripts/generate_datalake_manifest.py
python scripts/export_atlas_metadata.py
python scripts/run_bloc4_demo.py
```

## Fichiers repères Bloc 4
- `configs/datalake.yaml`
- `docs/block4_datalake.md`
- `docs/block4_governance.md`
- `docs/block4_referential_mapping.md`
- `airflow/dags/energy_datalake_batch.py`

## Références finales d'harmonisation
- `docs/final_harmonization.md`
- `docs/final_demo_path.md`
- `docs/api_contract.md`
