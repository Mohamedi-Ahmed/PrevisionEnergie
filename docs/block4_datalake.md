# Bloc 4 — Architecture Data Lake

## Objectif
Le Bloc 4 formalise l’extension Data Lake du projet sans casser l’architecture existante.

## Mapping retenu
- Bronze -> Raw
- Silver -> Curated
- Gold -> Consumption

## Zones
### Raw
- rôle : conservation de la donnée brute, traçabilité, rejouabilité
- chemin : `data/bronze`
- rétention : illimitée

### Curated
- rôle : données fiabilisées et harmonisées
- chemin : `data/silver`
- rétention : 5 ans

### Consumption
- rôle : tables analytiques, jeux de restitution, exposition API
- chemin : `data/gold`
- rétention : 2 ans

## Choix techniques V1
- stockage : logique compatible object storage, avec backend local et brique GCS déjà présente ;
- orchestration : chaîne batch existante, repositionnée comme Airflow-ready ;
- catalogue : Atlas retenu pour la V1 pédagogique ;
- tables structurées : préparation Delta Lake côté Gold.

## Fichiers repères
- `configs/datalake.yaml`
- `app/governance/rbac.py`
- `app/governance/lifecycle.py`
- `scripts/generate_datalake_manifest.py`
- `airflow/dags/energy_datalake_batch.py`
