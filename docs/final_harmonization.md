# Harmonisation finale du projet

## Version canonique à retenir
Le projet vise à anticiper la consommation quotidienne d'électricité et de gaz par région française à partir des données énergie, météo et calendaires.

- **Bloc 1** : cadrage du besoin, périmètre V1, parties prenantes, risques
- **Bloc 2** : pipeline data exécutable localement
- **Bloc 3** : couche Gold DWH en schéma en étoile + catalogue + SCD2
- **Bloc 4** : formalisation Data Lake gouvernée

## Vocabulaire final
- Bronze = Raw
- Silver = Curated
- Gold = Consumption

Dans la couche Gold :
- **Gold DWH** = fait + dimensions
- **Gold service dataset** = `gold_daily_features`

## Ce qui est implémenté
- pipeline batch local
- stockage local
- chargement SQL local SQLite
- API FastAPI
- schéma en étoile Gold
- SCD2 sur `dim_region`
- pack de métadonnées Atlas
- RBAC et rétention documentés et outillés

## Ce qui est préparé / documenté
- backend GCS
- Delta Lake côté Gold
- orchestration Airflow-ready
- lecture Data Lake gouvernée complète

## Ce qu'il ne faut pas survendre
- temps réel
- plateforme Atlas complète déployée
- Data Lake cloud industriel complet
- Delta Lake réellement déployé en production
- intégration complète des renouvelables
