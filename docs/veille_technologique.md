# Journal de veille technologique

**Projet** : PrevisionEnergie
**Responsable** : Ahmed Mohamedi
**Récurrence** : 1 h / semaine (vendredi après-midi)
**Outils d'agrégation** : Feedly (flux RSS), GitHub Trending, newsletters (Data Engineering Weekly, dbt blog)

---

## Semaine 1 — 10 janvier 2025

**Thème** : Architectures Data Lake modernes
**Sources consultées** :
- Databricks — "Medallion Architecture" (blog officiel)
- Article Medium — "Bronze, Silver, Gold layers explained"
- Documentation Delta Lake 3.x (changelog)

**Synthèse** :
L'architecture Medallion s'impose comme standard de facto pour structurer un Data Lake en couches. Le passage Bronze → Silver → Gold permet de séparer la donnée brute de la donnée fiabilisée. Delta Lake 3.x apporte l'Uniform format (Iceberg + Delta), mais pour un POC local SQLite reste suffisant avec la même logique en 3 couches.

**Action** : Adoption de l'architecture Medallion pour PrevisionEnergie.

---

## Semaine 2 — 17 janvier 2025

**Thème** : Comparaison des catalogues de métadonnées
**Sources consultées** :
- Apache Atlas — documentation officielle 2.3
- AWS Glue Data Catalog — page produit et pricing
- Google Dataplex — documentation et tutoriels

**Synthèse** :
Atlas reste le seul catalogue open-source mature avec lignage natif. Glue est très intégré à l'écosystème AWS mais vendor-locked. Dataplex couvre la gouvernance mais manque de maturité sur le glossaire. Pour un projet académique sans cloud, Atlas est le choix le plus défendable : on prépare un bundle JSON importable.

**Action** : Choix d'Atlas, préparation d'un bundle JSON (glossary + entities + lineage).

---

## Semaine 3 — 24 janvier 2025

**Thème** : Historisation dimensionnelle (SCD)
**Sources consultées** :
- Kimball Group — "Slowly Changing Dimensions" (article de référence)
- dbt docs — SCD Type 2 avec snapshots
- Stack Overflow — "SCD2 with SQLite limitations"

**Synthèse** :
Le SCD Type 2 est le mécanisme standard pour historiser les dimensions qui changent. Il nécessite valid_from/valid_to, is_current et un hash des attributs suivis. SQLite ne supporte pas les MERGE natifs, mais un pattern DELETE + INSERT ou UPDATE + INSERT fonctionne. dbt simplifie cela avec les snapshots, mais en pur Python on peut reproduire la logique avec un hash MD5.

**Action** : Implémentation du SCD2 sur dim_region avec attr_hash_md5.

---

## Semaine 4 — 31 janvier 2025

**Thème** : Frameworks API pour Data Engineering
**Sources consultées** :
- FastAPI — documentation officielle (tiangolo)
- Comparatif FastAPI vs Flask vs Django REST (Real Python)
- OpenAPI 3.1 spec

**Synthèse** :
FastAPI offre le meilleur rapport productivité / documentation automatique pour un projet data. La génération automatique de /docs (Swagger UI) et /redoc, le typage Pydantic et l'injection de dépendances en font le choix naturel. Flask reste plus simple mais sans validation intégrée. Django REST est surdimensionné pour une API de lecture.

**Action** : Adoption de FastAPI avec Bearer token pour l'API PrevisionEnergie.

---

## Semaine 5 — 7 février 2025

**Thème** : Orchestration batch et Airflow
**Sources consultées** :
- Apache Airflow — documentation 2.8
- Article — "Airflow vs Prefect vs Dagster" (comparatif 2024)
- Astronomer blog — bonnes pratiques DAG

**Synthèse** :
Airflow reste le standard d'orchestration batch en entreprise malgré la montée de Prefect et Dagster. Le modèle DAG est adapté à notre pipeline séquentiel (init → transform → load → gold → manifest → atlas). Pour un POC local, un DAG déclaratif suffit sans déployer le scheduler complet.

**Action** : Création du DAG energy_datalake_batch.py avec 6 tâches chaînées.

---

## Semaine 6 — 14 février 2025

**Thème** : Qualité des données et observabilité
**Sources consultées** :
- Great Expectations — documentation et gallery
- Article — "Data quality dimensions" (DAMA)
- Monte Carlo — "Data Observability 101"

**Synthèse** :
La qualité des données se mesure sur 6 dimensions : complétude, exactitude, cohérence, fraîcheur, unicité, validité. Great Expectations est puissant mais lourd pour un POC. Une approche légère avec des quality reports JSON (taux de nulls, outliers IQR, volumétrie) couvre les besoins de la V1 sans dépendance lourde.

**Action** : Implémentation des quality reports JSON dans le pipeline Silver.

---

## Semaine 7 — 21 février 2025

**Thème** : RGPD et éco-responsabilité dans les projets data
**Sources consultées** :
- CNIL — guide RGPD pour les développeurs
- RGESN — Référentiel Général d'Écoconception (DINUM)
- INR — bonnes pratiques numérique responsable

**Synthèse** :
Même sans données personnelles, les principes RGPD de minimisation et de finalité s'appliquent au design. Le RGESN propose 6 axes d'écoconception applicables aux pipelines data : sobriété du stockage, optimisation des traitements, choix d'infrastructure proportionnée, réduction des transferts, outillage léger, sélection de prestataires responsables.

**Action** : Intégration des 6 principes RGESN dans E2 et E7.

---

## Semaine 8 — 28 février 2025

**Thème** : Monitoring et alerting pour pipelines data
**Sources consultées** :
- Prometheus + Grafana — documentation officielle
- Article — "Monitoring data pipelines" (Datadog blog)
- Python logging — module standard et bonnes pratiques

**Synthèse** :
En production, Prometheus collecte les métriques et Grafana les affiche avec des seuils d'alerte. Pour un POC local, le module logging Python avec catégorisation (INFO/WARNING/ERROR/CRITICAL) et des health checks périodiques suffisent. L'essentiel est de montrer la logique : vérifier la fraîcheur, la volumétrie, l'état de la base, et déclencher une alerte si un seuil est franchi.

**Action** : Création du module monitoring.py avec alertes catégorisées et health checks.

---

## Synthèse communiquée aux parties prenantes

| Date | Destinataire | Objet | Format |
|------|-------------|-------|--------|
| 31/01/2025 | DSI | Choix d'architecture Medallion + Atlas | Note technique (mail) |
| 14/02/2025 | Direction | Avancement pipeline et qualité données | Compte-rendu sprint review |
| 28/02/2025 | Équipe | Stack retenue (FastAPI, Airflow, RBAC) | Présentation interne |
| 07/03/2025 | DPO | Conformité RGPD et éco-responsabilité | Note de synthèse |
