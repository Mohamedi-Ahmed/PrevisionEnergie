# E6 / E7 - Statut reel

## Reellement implemente

- SCD2 sur `dim_region` dans `app/db/loaders/gold_loader.py`
- RBAC simple par roles dans `app/governance/rbac.py`
- Retention par zone dans `app/governance/lifecycle.py`
- Manifest datalake genere par `scripts/generate_datalake_manifest.py`
- Monitoring et alertes locales dans `app/governance/monitoring.py`
- Backup local dans `scripts/backup_db.py`
- Bundle Atlas exportable dans `atlas/` et `scripts/export_atlas_metadata.py`

## Squelette propre / preparation

- Serveur Apache Atlas live non deploie dans le repo
- Import automatique du bundle dans Atlas non implemente
- RBAC non branche a un vrai IAM, juste une matrice de permissions locale
- Retention non appliquee automatiquement sur le filesystem, seulement formalisee et testee
- Gouvernance cloud et policies centralisees non deployees

## Comment le presenter a l'oral

- Dire clairement que la gouvernance locale est runnable et demonstrable
- Dire qu'Atlas est prepare sous forme de bundle JSON exportable, pas comme plateforme complete
- Dire que le SCD2 est bien code et teste sur `dim_region`
- Dire que le manifest et les regles RBAC / retention servent de base de gouvernance exploitable localement
