# Plan de communication -- Projet PrevisionEnergie

## Principe

Chaque interlocuteur recoit une communication adaptee a son niveau technique et a ses preoccupations. Les supports respectent les recommandations d'accessibilite (contraste, taille de police, structure claire).

---

## Matrice de communication

| Destinataire | Preoccupation principale | Format | Frequence | Contenu adapte |
|-------------|-------------------------|--------|-----------|----------------|
| **Direction / CODIR** | ROI, planning, risques | Slide deck executif (5 slides max) | Mensuel + jalons | Avancement vs planning, budget consomme, risques majeurs, decisions a prendre |
| **DSI / Architecte** | Conformite technique, integration SI | Document technique + schema d'architecture | Bi-mensuel | Stack technique, choix d'architecture, integration avec le SI existant, plan de deploiement |
| **DPO** | Conformite RGPD, donnees personnelles | Registre RGPD + note de synthese | A chaque evolution + trimestriel | Registre des traitements, analyse d'impact (PIA si necessaire), mesures de securite |
| **Equipe Data** | Specifications, Sprint goals, blocages | Daily standup + Sprint review + doc technique | Quotidien (standup) + bi-hebdo (sprint) | User stories, taches du sprint, documentation API, quality reports |
| **Equipe ML / Data Science** | Qualite des donnees, features disponibles | API contract + data dictionary | A chaque livraison | Endpoints disponibles, schema des features, quality reports Silver |
| **Utilisateurs finaux** | Fiabilite, acces, formation | Guide utilisateur + session de demo | A la livraison + accompagnement | Swagger UI, exemples d'appels API, FAQ |

---

## Etapes de communication planifiees

| Jalon projet | Communication | Destinataire | Support |
|-------------|---------------|-------------|---------|
| **Lancement** (Sprint 0) | Reunion de lancement : contexte, objectifs, planning | Tous | Presentation + feuille de route |
| **Fin Sprint 1** (Bronze) | Pipeline d'ingestion operationnel | DSI + Equipe Data | Demo live + doc technique |
| **Fin Sprint 2** (Silver) | Donnees nettoyees disponibles | Equipe ML + DPO | Data dictionary + registre RGPD |
| **Fin Sprint 3** (Gold/DWH) | Entrepot de donnees operationnel | Direction + DSI | Schema etoile + KPIs disponibles |
| **Fin Sprint 4** (API) | API REST fonctionnelle | Tous | Demo Swagger + guide utilisateur |
| **Fin Sprint 5** (Data Lake) | Gouvernance Data Lake formalisee | DSI + DPO | Architecture zones + RBAC + retention |
| **Livraison finale** | Bilan projet | Direction + tous | Presentation finale + documentation complete |

---

## Supports par interlocuteur

### Direction / CODIR
- **Format** : PowerPoint executif, 5 slides max
- **Contenu** : contexte en 1 phrase, avancement visuel (vert/orange/rouge), budget, risques top 3, decisions requises
- **Ton** : strategique, oriente resultats et valeur metier
- **Accessibilite** : police 18pt min, contraste eleve, pas de jargon technique

### DSI / Architecte
- **Format** : Document Markdown + schemas d'architecture (draw.io / Mermaid)
- **Contenu** : choix techniques justifies, schemas (fonctionnel, applicatif, infrastructure), plan de deploiement
- **Ton** : technique, oriente decisions d'architecture
- **Accessibilite** : schemas avec alt-text, structure par titres navigables

### DPO
- **Format** : Registre RGPD (tableau structure) + note de synthese 1 page
- **Contenu** : traitements de donnees, base legale, mesures de securite, analyse d'impact si necessaire
- **Ton** : reglementaire, oriente conformite
- **Accessibilite** : document structure, references aux articles RGPD

### Equipe Data Engineering
- **Format** : Documentation technique (Markdown dans le repo), README, docstrings
- **Contenu** : architecture, API contract, data dictionary, procedures d'installation
- **Ton** : technique et operationnel
- **Accessibilite** : versionne dans Git, navigable, exemples de code

---

## Gestion des retours

Les retours des parties prenantes sont integres au processus projet :
1. **Sprint review** : retours collectes en fin de sprint, priorises dans le backlog
2. **Canal Slack/Teams** : questions ponctuelles, reponse sous 24h
3. **Bilan de jalon** : retours formalises, actions tracees dans le board Scrum
