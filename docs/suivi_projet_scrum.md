# Suivi de projet Scrum -- PrevisionEnergie

## Organisation Scrum

| Element | Valeur |
|---------|--------|
| **Duree de sprint** | 2 semaines |
| **Rituels** | Daily standup (15 min), Sprint planning, Sprint review, Retrospective |
| **Outil de suivi** | Trello / Jira (board Kanban avec colonnes : Backlog, To Do, In Progress, Review, Done) |
| **Estimation** | Poker planning (suite de Fibonacci : 1, 2, 3, 5, 8, 13) |
| **Indicateurs** | Velocity, Burndown chart, taux de completion |

---

## Backlog et Sprints

### Sprint 0 -- Cadrage (Semaines 1-2)
**Objectif** : Analyser le besoin, cadrer le projet, planifier

| User Story | Points | Statut |
|-----------|--------|--------|
| Conduire les entretiens (Direction, DSI, DPO, Service donnees) | 3 | Done |
| Rediger la note de synthese (5 parties) | 5 | Done |
| Cartographier les sources de donnees (4 dimensions) | 3 | Done |
| Produire l'etude technique d'architecture | 8 | Done |
| Planifier la feuille de route (sprints, jalons) | 3 | Done |

**Velocity** : 22 points | **Completion** : 100%

---

### Sprint 1 -- Ingestion Bronze (Semaines 3-4)
**Objectif** : Pipeline d'extraction multi-sources operationnel

| User Story | Points | Statut |
|-----------|--------|--------|
| Implementer KaggleExtractor (CSV) | 3 | Done |
| Implementer RTEExtractor (API REST) | 5 | Done |
| Implementer MeteoFranceExtractor (API) | 5 | Done |
| Implementer DataGouvExtractor (API) | 3 | Done |
| Creer l'abstraction StorageBackend (local + GCS) | 5 | Done |
| Ecrire les tests unitaires ingestion | 3 | Done |
| Versionner sur Git + documentation | 2 | Done |

**Velocity** : 26 points | **Completion** : 100%

---

### Sprint 2 -- Transformation Silver (Semaines 5-6)
**Objectif** : Pipeline Bronze -> Silver complet avec qualite

| User Story | Points | Statut |
|-----------|--------|--------|
| Pipeline de nettoyage (typage, normalisation, deduplication) | 8 | Done |
| Imputation des valeurs manquantes | 3 | Done |
| Detection et traitement des outliers (IQR) | 3 | Done |
| Calcul DJU (Degree-Day Units) | 3 | Done |
| Calendar features (weekend, mois, jour semaine) | 2 | Done |
| Quality reports JSON par fichier | 3 | Done |
| Tests unitaires processing | 5 | Done |

**Velocity** : 27 points | **Completion** : 100%

---

### Sprint 3 -- DWH Gold + API (Semaines 7-8)
**Objectif** : Entrepot de donnees en etoile + API REST

| User Story | Points | Statut |
|-----------|--------|--------|
| DDL schema en etoile (1 fait + 4 dimensions) | 5 | Done |
| ETL Silver -> Gold (MERGE upsert idempotent) | 8 | Done |
| SCD Type 2 sur dim_region | 5 | Done |
| API FastAPI avec 5 routers | 8 | Done |
| Authentification Bearer token | 3 | Done |
| Tests integration API + ETL | 5 | Done |
| Documentation OpenAPI + API contract | 2 | Done |

**Velocity** : 36 points | **Completion** : 100%

---

### Sprint 4 -- Data Lake et Gouvernance (Semaines 9-10)
**Objectif** : Formaliser le Data Lake, RBAC, lifecycle, catalogue

| User Story | Points | Statut |
|-----------|--------|--------|
| Architecture Data Lake 3 zones (Raw/Curated/Consumption) | 3 | Done |
| RBAC 3 roles (reader/engineer/admin) | 3 | Done |
| Politique de retention par zone | 2 | Done |
| Pack metadata Apache Atlas (glossaire, entities, lignage) | 8 | Done |
| DAG Airflow batch quotidien | 5 | Done |
| Comparaison catalogues (Atlas vs Glue vs Dataplex) | 3 | Done |
| Delta Lake DDL (cible de deploiement) | 3 | Done |
| Tests RBAC + lifecycle | 3 | Done |

**Velocity** : 30 points | **Completion** : 100%

---

### Sprint 5 -- Finalisation et Soutenance (Semaines 11-12)
**Objectif** : Documentation, tests finaux, preparation soutenance

| User Story | Points | Statut |
|-----------|--------|--------|
| Rapports professionnels E2-E7 | 13 | Done |
| Registre RGPD formel | 2 | Done |
| Document de veille technologique | 3 | Done |
| Plan de communication multi-interlocuteurs | 2 | Done |
| Presentation PowerPoint finale | 5 | Done |
| Demo setup script (run_demo_setup.py) | 3 | Done |
| Revue de code et audit | 3 | Done |

**Velocity** : 31 points | **Completion** : 100%

---

## Indicateurs d'avancement

### Velocity par sprint

```
Sprint 0 : ████████████████████████ 22 pts
Sprint 1 : ██████████████████████████ 26 pts
Sprint 2 : ███████████████████████████ 27 pts
Sprint 3 : ████████████████████████████████████ 36 pts
Sprint 4 : ██████████████████████████████ 30 pts
Sprint 5 : ███████████████████████████████ 31 pts
```

**Velocity moyenne** : 28.7 points / sprint

### Burndown chart (Sprint 3 -- exemple)

```
Points restants
40 |*
35 |  *
30 |    *
25 |      *    (rythme ideal)
20 |        *
15 |     .    *
10 |       .    *
 5 |         .    *
 0 |___________.__.*__
    J1  J3  J5  J7  J9  J10
    
* = ideal    . = reel (leger retard rattrape en fin de sprint)
```

### Taux de completion global

| Metrique | Valeur |
|----------|--------|
| User stories totales | 47 |
| User stories completees | 47 |
| Points totaux | 172 |
| Points livres | 172 |
| **Taux de completion** | **100%** |

---

## Gestion des risques rencontres

| Sprint | Risque | Impact | Resolution |
|--------|--------|--------|------------|
| Sprint 1 | API RTE indisponible temporairement | Moyen | Fallback sur donnees Kaggle, retry avec backoff |
| Sprint 2 | Donnees meteo avec beaucoup de valeurs manquantes | Faible | Imputation par mediane regionale implementee |
| Sprint 3 | Complexite du SCD2 sous-estimee | Moyen | Reestimation de 3 a 5 points, livrée dans le sprint |
| Sprint 4 | Atlas necessite une infra lourde pour demo | Faible | Export JSON simulant l'integration (atlas_bundle.json) |
