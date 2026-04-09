import logging
import logging.config
from pathlib import Path

import yaml


BASE_DIR = Path(__file__).resolve().parents[2]
LOGGING_CONFIG_PATH = BASE_DIR / "configs" / "logging.yaml"


def setup_logging() -> None:
    if LOGGING_CONFIG_PATH.exists():
        with LOGGING_CONFIG_PATH.open("r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=logging.INFO)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
