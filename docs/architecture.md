# Architecture

## Lecture canonique du projet

Le projet suit une logique de montée en maturité continue :
- **Bloc 2** : pipeline data exécutable localement, ingestion, Bronze, Silver, chargement SQL local et API FastAPI ;
- **Bloc 3** : ajout d'une vraie couche **Gold DWH** en schéma en étoile, tout en conservant `gold_daily_features` comme table de restitution ;
- **Bloc 4** : formalisation du même socle sous forme de **Data Lake gouverné**.

## Couches
- **Bronze** : données brutes, traçabilité, rejouabilité
- **Silver** : données nettoyées, normalisées et enrichies
- **Gold** :
  - tables analytiques / décisionnelles (DWH)
  - dataset de service `gold_daily_features` pour restitution / API

## Mapping Bloc 4
- Bronze -> Raw
- Silver -> Curated
- Gold -> Consumption

## Implémentation locale et cible
- stockage local par défaut via `LocalStorageBackend`
- compatibilité GCS préparée via `GCSStorageBackend`
- couche SQL locale démontrable en **SQLite**
- cible analytique avancée documentée en **Delta Lake**

## Principe de soutenance
Toujours distinguer :
- ce qui est **implémenté** ;
- ce qui est **documenté / préparé** ;
- ce qui est **proposé pour la suite**.
