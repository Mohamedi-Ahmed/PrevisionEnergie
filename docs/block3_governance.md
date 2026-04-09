# Bloc 3 - Gouvernance, catalogue et SCD2

Ce document complète l’extension Bloc 3 du projet.

## Catalogue de données
Le projet est préparé pour une déclaration dans Apache Atlas autour de quatre axes :
- sémantique ;
- modèles ;
- flux / lignage ;
- accès.

## Lignage cible
Kaggle / APIs -> Bronze -> Silver -> Gold DWH -> API

## SCD2
`dim_region` embarque les colonnes :
- `valid_from`
- `valid_to`
- `is_current`
- `attr_hash_md5`

Le loader Gold compare le hash courant à la version en base. En cas de variation :
- la ligne courante est clôturée ;
- une nouvelle version est insérée.
