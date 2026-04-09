from fastapi import FastAPI

from app.api.routers import auth, consumption, features, health, metadata
from app.core.config import get_settings


settings = get_settings()
api_config = settings.load_yaml("settings.yaml").get("api", {})

app = FastAPI(
    title=api_config.get("title", "Energy Forecast API"),
    version=api_config.get("version", "0.1.0"),
    description=(
        "API Bloc 2 pour exposer des données énergie / météo nettoyées "
        "et des features calculées à partir de la couche Silver."
    ),
    docs_url=api_config.get("docs_url", "/docs"),
    redoc_url=api_config.get("redoc_url", "/redoc"),
    openapi_tags=[
        {"name": "health", "description": "API health and runtime status."},
        {"name": "auth", "description": "Minimal authentication endpoints."},
        {"name": "consumption", "description": "Daily consumption access endpoints (C9)."},
        {"name": "features", "description": "Feature access endpoints for analytics and future ML (C10)."},
        {"name": "metadata", "description": "Reference metadata endpoints."},
    ],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(consumption.router)
app.include_router(features.router)
app.include_router(metadata.router)
