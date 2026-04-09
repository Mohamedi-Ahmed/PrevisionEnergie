# Comparaison des catalogues de donnees -- PrevisionEnergie

## Contexte

Le choix d'un catalogue de donnees est un element cle du Bloc 4 (C18). Trois solutions ont ete evaluees selon les contraintes du projet : budget limite, equipe reduite, architecture Medallion, conformite RGPD.

## Tableau comparatif

| Critere                        | Apache Atlas                  | AWS Glue Data Catalog          | Google Dataplex               |
|-------------------------------|-------------------------------|-------------------------------|-------------------------------|
| **Editeur**                   | Apache Foundation (open source) | Amazon Web Services           | Google Cloud Platform         |
| **Licence / Cout**            | Gratuit (Apache 2.0)         | Pay-per-use (~1$/100k objets/mois) | Pay-per-use (~variable)     |
| **Modele de deploiement**     | On-premise / VM / Docker     | SaaS (AWS uniquement)         | SaaS (GCP uniquement)        |
| **Lock-in fournisseur**       | Aucun                        | Fort (ecosysteme AWS)         | Fort (ecosysteme GCP)        |
| **Glossaire metier**          | Oui (natif)                  | Non (via DataBrew ou externe) | Oui (Business Glossary)      |
| **Lignage (lineage)**         | Oui (natif, graphe complet)  | Partiel (jobs Glue seulement) | Oui (natif, multi-source)    |
| **Classification des donnees**| Oui (tags, labels, types)    | Oui (classifiers, crawlers)   | Oui (auto-discovery)         |
| **Integration Delta Lake**    | Oui (via hooks Spark/Hive)   | Oui (natif avec Glue ETL)     | Oui (via BigLake)            |
| **Integration Airflow**       | Oui (API REST + hooks)       | Oui (operateurs Airflow)      | Oui (operateurs Airflow)     |
| **API REST**                  | Oui (complete)               | Oui (SDK AWS)                 | Oui (SDK GCP)                |
| **Recherche / Index**         | Oui (Solr/Elasticsearch)     | Oui (recherche integree)      | Oui (recherche unifiee)      |
| **RBAC / Securite**           | Oui (Ranger integration)     | Oui (IAM AWS)                 | Oui (IAM GCP)                |
| **Conformite RGPD**           | A configurer manuellement    | Oui (Macie + Lake Formation)  | Oui (DLP + Data Catalog)     |
| **Complexite de mise en place**| Elevee (infra a gerer)      | Faible (SaaS manage)          | Faible (SaaS manage)         |
| **Communaute / Documentation**| Large (Apache ecosystem)     | Large (AWS ecosystem)         | Moyenne (plus recent)        |
| **Scalabilite**               | Horizontale (Hadoop/K8s)     | Automatique (serverless)      | Automatique (serverless)     |

## Analyse pour PrevisionEnergie

### Pourquoi Apache Atlas a ete choisi

1. **Cout zero** : projet a budget contraint, pas de frais cloud recurrents
2. **Pas de lock-in** : le client peut migrer vers n'importe quel cloud sans changer de catalogue
3. **Lignage natif complet** : graphe de lignage bout en bout (Kaggle -> Bronze -> Silver -> Gold -> API), pas limite aux jobs d'un seul outil
4. **Glossaire metier integre** : les termes metier (consommation, DJU, region) sont documentes dans le catalogue, pas dans un outil tiers
5. **Coherence avec la stack** : Atlas s'integre avec Spark/Delta Lake (cible de production) et Airflow (orchestrateur)

### Limites acceptees

- **Complexite d'installation** : Atlas necessite une infrastructure (Kafka, HBase/Solr). Pour le projet, un export JSON simulant l'integration a ete produit (`atlas/atlas_bundle.json`)
- **Pas de SaaS** : maintenance a la charge de l'equipe data, mais coherent avec la politique de l'organisation (donnees sensibles on-premise)

### Dans quels cas on aurait choisi autrement

| Situation                                    | Choix recommande |
|---------------------------------------------|-----------------|
| Organisation 100% AWS, budget disponible     | AWS Glue        |
| Organisation 100% GCP, besoin auto-discovery | Dataplex        |
| Equipe reduite, besoin open-source, multi-cloud | **Atlas** (choix actuel) |
| PME sans equipe infra, besoin rapide         | Dataplex (SaaS simple) |

## Conclusion

Le choix d'Atlas est motive par le besoin d'independance technologique et la richesse fonctionnelle (lignage + glossaire). La mise en production necessiterait un deploiement Docker/K8s que le projet prepare via les fichiers `atlas/` mais ne deploie pas en environnement de demonstration.
