# Veille technologique et reglementaire -- PrevisionEnergie

## Organisation de la veille

| Element | Detail |
|---------|--------|
| **Frequence** | 1h minimum par semaine (vendredi matin) |
| **Thematiques** | ML energetique, Delta Lake / Lakehouse, Reglementation donnees (RGPD, AI Act) |
| **Outils** | Feedly (agregation RSS), LinkedIn (communautes Data), GitHub Releases, newsletters |
| **Format de sortie** | Synthese mensuelle + alertes ponctuelles si impact projet |

---

## Thematiques de veille

### 1. Machine Learning applique a l'energie
- Modeles de prevision de consommation (LSTM, Prophet, XGBoost)
- Feature engineering specifique energie (DJU, lags, rolling averages)
- Benchmarks de precision sur donnees RTE/eco2mix

### 2. Delta Lake et architecture Lakehouse
- Evolution du format Delta Lake (versions, fonctionnalites)
- Comparaison Delta Lake vs Apache Iceberg vs Apache Hudi
- Patterns MERGE / UPSERT pour idempotence
- OPTIMIZE et ZORDER : cas d'usage et benchmarks

### 3. Reglementation donnees
- RGPD : evolutions, sanctions, bonnes pratiques
- AI Act europeen : impact sur les projets data/ML
- Donnees energetiques : reglementations sectorielles (RTE, CRE)

---

## Syntheses de veille realisees

### Janvier 2026 -- Delta Lake 4.0 et impact sur l'architecture

**Source** : Blog Databricks, GitHub delta-io/delta, Documentation officielle

**Synthese** :
Delta Lake 4.0 introduit le support natif des liquid clusters (remplacement de ZORDER), l'amelioration des performances de MERGE (jusqu'a 3x plus rapide sur les upserts), et la compatibilite UniForm v2 pour la lecture Iceberg/Hudi.

**Impact projet** : La migration vers Delta Lake (actuellement documentee dans `sql/delta/create_gold_tables_delta.sql`) beneficiera directement de ces optimisations. Le MERGE idempotent du gold_loader.py est deja conforme au pattern recommande.

**Action** : Aucune modification immediate. A integrer lors de la phase de deploiement cloud.

---

### Fevrier 2026 -- RGPD et donnees energetiques agregees

**Source** : CNIL (cnil.fr), Documentation RTE Open Data

**Synthese** :
La CNIL confirme que les donnees de consommation energetique agregees au niveau regional ne constituent pas des donnees personnelles au sens du RGPD, a condition que le grain d'agregation soit suffisant (pas de maille infra-communale pour les zones a faible densite). Les donnees eco2mix de RTE sont classees "donnees ouvertes" et ne necessitent pas de base legale specifique.

**Impact projet** : Confirmation que l'approche "privacy by design" du projet est correcte. Les donnees collectees (consommation regionale quotidienne) ne sont pas des donnees personnelles. Le registre RGPD a ete mis a jour en consequence.

**Action** : Documenter cette analyse dans le registre RGPD (fait).

---

### Mars 2026 -- Apache Atlas vs alternatives cloud

**Source** : Documentation Atlas 2.3, AWS Glue documentation, Google Dataplex GA release notes

**Synthese** :
Apache Atlas reste la reference open-source pour le lignage de donnees. Google Dataplex a atteint la GA (general availability) avec des fonctionnalites de decouverte automatique. AWS Glue Data Catalog reste limite en lignage (uniquement les jobs Glue).

**Impact projet** : Le choix d'Atlas est confirme pour un contexte multi-cloud / on-premise. Un tableau comparatif Atlas vs Glue vs Dataplex a ete produit (voir `docs/comparaison_catalogues.md`).

**Action** : Tableau comparatif integre au rapport E7.

---

### Avril 2026 -- AI Act et projets data en entreprise

**Source** : EUR-Lex, Blog CNIL, Documentation Commission Europeenne

**Synthese** :
L'AI Act europeen (entree en vigueur progressive 2024-2026) impose des exigences de transparence et de gouvernance pour les systemes d'IA. Les systemes de prevision energetique sont classes "risque limite" (pas "haut risque"), mais les exigences de documentation et de tracabilite s'appliquent.

**Impact projet** : Le pipeline PrevisionEnergie integre deja la tracabilite (quality reports, lignage Atlas, versionnement Git). La documentation des choix d'architecture et des donnees utilisees est conforme aux attendus de l'AI Act pour les systemes a risque limite.

**Action** : Mentionner l'AI Act dans la section gouvernance du rapport E7.

---

## Sources de veille regulieres

| Source | Type | Frequence de consultation |
|--------|------|--------------------------|
| Databricks Blog | Blog technique | Hebdomadaire |
| Delta Lake GitHub Releases | Changelog | Bi-mensuelle |
| CNIL Actualites | Reglementation | Bi-mensuelle |
| RTE Open Data changelog | Donnees metier | Mensuelle |
| Data Engineering Weekly (newsletter) | Agregation | Hebdomadaire |
| LinkedIn Data Engineering France | Communaute | Quotidienne |
| Towards Data Science (Medium) | Articles | Hebdomadaire |
| Apache Atlas JIRA | Bugs/features | Mensuelle |
