# Registre des traitements de donnees -- PrevisionEnergie

*Document etabli conformement a l'article 30 du RGPD (Reglement UE 2016/679)*

---

## 1. Identite du responsable de traitement

| Champ | Valeur |
|-------|--------|
| Organisation | PrevisionEnergie (operateur energetique -- fictif) |
| Responsable de traitement | Direction des Systemes d'Information |
| DPO (Delegue a la Protection des Donnees) | DPO designe (contact : dpo@previenergie.fr) |
| Sous-traitant technique | Equipe Data Engineering (Ahmed Mohamedi) |

---

## 2. Inventaire des traitements

### Traitement 1 : Ingestion des donnees de consommation energetique

| Champ | Description |
|-------|-------------|
| **Finalite** | Collecter les donnees de consommation electrique regionales pour alimenter un modele de prevision |
| **Base legale** | Interet legitime (optimisation de la production energetique) |
| **Categories de donnees** | Consommation electrique agregee par region et par jour (MW), temperatures moyennes, metadata calendaire |
| **Donnees personnelles** | **Aucune** -- toutes les donnees sont agregees au niveau regional, aucune donnee individuelle n'est collectee |
| **Source des donnees** | RTE (eco2mix), Kaggle (jeux publics), Meteo-France (API publique), data.gouv.fr |
| **Destinataires** | Equipe Data (interne), Direction Strategie (via API), equipe ML (via Gold layer) |
| **Transfert hors UE** | Non -- stockage local ou GCS region europe-west1 (si cloud) |
| **Duree de conservation** | Bronze : illimitee / Silver : 5 ans / Gold : 2 ans |
| **Mesures de securite** | Authentification Bearer token sur l'API, RBAC par role, pas d'acces direct a la base |

### Traitement 2 : Transformation et enrichissement (Bronze -> Silver)

| Champ | Description |
|-------|-------------|
| **Finalite** | Nettoyer, normaliser et enrichir les donnees brutes pour les rendre exploitables |
| **Base legale** | Interet legitime |
| **Categories de donnees** | Donnees energetiques agregees, donnees meteorologiques, indicateurs calcules (DJU, rolling avg) |
| **Donnees personnelles** | **Aucune** |
| **Traitements appliques** | Nettoyage (typage, deduplication), normalisation (noms de regions), imputation, detection d'outliers, calcul DJU |
| **Destinataires** | Couche Gold (DWH), equipe Data |
| **Duree de conservation** | 5 ans (politique Silver/Curated) |
| **Mesures de securite** | Versionnement Git, quality reports JSON par fichier, logs d'execution |

### Traitement 3 : Chargement DWH et restitution (Silver -> Gold -> API)

| Champ | Description |
|-------|-------------|
| **Finalite** | Alimenter l'entrepot de donnees et exposer les donnees via API REST pour les equipes metier |
| **Base legale** | Interet legitime |
| **Categories de donnees** | Faits de consommation quotidienne, dimensions (date, region, energie, contexte meteo) |
| **Donnees personnelles** | **Aucune** |
| **Traitements appliques** | MERGE upsert idempotent, SCD Type 2 sur dim_region, calcul d'agregats |
| **Destinataires** | Equipe Strategie (via API), equipe ML (via gold_daily_features), tableaux de bord |
| **Duree de conservation** | 2 ans (politique Gold/Consumption) |
| **Mesures de securite** | API avec authentification Bearer, RBAC 3 niveaux, journalisation des acces |

---

## 3. Analyse des risques et mesures

| Risque | Probabilite | Impact | Mesure mise en place |
|--------|------------|--------|---------------------|
| Acces non autorise aux donnees | Faible | Moyen | Authentification Bearer + RBAC par role |
| Fuite de donnees personnelles | **Tres faible** | Eleve | Aucune donnee personnelle collectee (privacy by design) |
| Perte de donnees | Faible | Moyen | Bronze illimite (rejouabilite), backup planifie |
| Non-conformite retention | Faible | Moyen | Politique de lifecycle automatisee (5 ans Silver, 2 ans Gold) |
| Transfert hors UE non autorise | Faible | Eleve | Stockage local ou GCS europe-west1 uniquement |

---

## 4. Privacy by design -- Principes appliques

1. **Minimisation** : seules les donnees necessaires sont collectees (pas de donnees individuelles, uniquement des agregats regionaux)
2. **Pseudonymisation** : non applicable (pas de donnees personnelles)
3. **Limitation de la conservation** : politique de retention differenciee par zone (Bronze illimite, Silver 5 ans, Gold 2 ans)
4. **Integrite et confidentialite** : authentification API, RBAC, versionnement des scripts
5. **Transparence** : documentation complete (data dictionary, API contract, ce registre)

---

## 5. Historique des mises a jour

| Date | Modification | Auteur |
|------|-------------|--------|
| 2026-01-15 | Creation initiale du registre | Ahmed Mohamedi |
| 2026-03-20 | Ajout traitement Gold/DWH (Bloc 3) | Ahmed Mohamedi |
| 2026-04-05 | Ajout politique Data Lake (Bloc 4) | Ahmed Mohamedi |
