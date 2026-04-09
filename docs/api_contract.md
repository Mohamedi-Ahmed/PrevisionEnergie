# API Contract

## Positionnement
API de démonstration exposant les données préparées dans la couche SQL locale.

## Endpoints actuels
- `GET /health`
- `POST /api/v1/auth/token`
- `GET /api/v1/consumption`
- `GET /api/v1/features`
- `GET /api/v1/metadata/regions`

## Sécurité
Les endpoints métier sont protégés par Bearer token.

## Posture de démonstration
Pendant la soutenance, montrer les routes réellement exposées dans Swagger / OpenAPI et éviter les anciens libellés génériques du type `/v1/regions` ou `/v1/metadata`.
