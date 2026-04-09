import sqlite3
from pathlib import Path

from app.core.config import BASE_DIR, get_settings
from app.core.exceptions import DatabaseError



def get_sqlite_database_path() -> Path:
    settings = get_settings()
    url = settings.database_url

    if not url.startswith("sqlite:///"):
        raise DatabaseError(
            "Only sqlite:/// URLs are supported by the current lightweight API repository layer."
        )

    raw_path = url.replace("sqlite:///", "", 1)
    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = BASE_DIR / db_path
    return db_path



def get_connection() -> sqlite3.Connection:
    db_path = get_sqlite_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection
