# Bloc 4 — Gouvernance Data Lake

## RBAC
### data_reader
- lecture : curated, consumption, metadata
- écriture : aucune

### data_engineer
- lecture : raw, curated, consumption, metadata
- écriture : raw, curated, consumption, metadata

### data_admin
- lecture : toutes les zones
- écriture : toutes les zones
- administration : toutes les zones

## Cycle de vie
- Raw : illimité
- Curated : 5 ans
- Consumption : 2 ans

## Contrôles identifiés
- fraîcheur des données ;
- fichier manquant ;
- dérive de volumétrie ;
- cohérence des droits d’accès.

## Conformité
Le projet manipule principalement des données non nominatives et agrégées. La logique privacy by design définie dans les blocs précédents est conservée.
