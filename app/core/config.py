from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "configs"


class Settings(BaseSettings):
    app_env: str = Field(default="dev", alias="APP_ENV")
    app_name: str = Field(default="prevision-energie-api", alias="APP_NAME")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_log_level: str = Field(default="INFO", alias="APP_LOG_LEVEL")

    api_bearer_token: str = Field(default="demo-token-change-me", alias="API_BEARER_TOKEN")
    api_auth_username: str = Field(default="demo_user", alias="API_AUTH_USERNAME")
    api_auth_password: str = Field(default="demo_password_change_me", alias="API_AUTH_PASSWORD")

    storage_backend: str = Field(default="local", alias="STORAGE_BACKEND")
    local_data_dir: str = Field(default="./data", alias="LOCAL_DATA_DIR")

    database_url: str = Field(default="sqlite:///./prevision_energie.db", alias="DATABASE_URL")

    rte_api_base_url: str | None = Field(default=None, alias="RTE_API_BASE_URL")
    rte_api_key: str | None = Field(default=None, alias="RTE_API_KEY")
    meteo_france_api_base_url: str | None = Field(default=None, alias="METEO_FRANCE_API_BASE_URL")
    meteo_france_api_key: str | None = Field(default=None, alias="METEO_FRANCE_API_KEY")
    data_gouv_base_url: str | None = Field(default=None, alias="DATA_GOUV_BASE_URL")
    kaggle_dataset: str | None = Field(default=None, alias="KAGGLE_DATASET")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def load_yaml(self, filename: str) -> dict[str, Any]:
        path = CONFIG_DIR / filename
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as file:
            return yaml.safe_load(file) or {}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
