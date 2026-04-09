import sqlite3
from pathlib import Path

from app.db.connection import get_sqlite_database_path


class SQLRunner:
    def __init__(self) -> None:
        self.db_path = get_sqlite_database_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def run_file(self, file_path: str) -> None:
        path = Path(file_path)
        sql = path.read_text(encoding="utf-8")
        if not sql.strip():
            return
        with sqlite3.connect(self.db_path) as connection:
            connection.executescript(sql)
            connection.commit()

    def run_directory(self, directory_path: str) -> None:
        directory = Path(directory_path)
        if not directory.is_absolute():
            from app.core.config import BASE_DIR
            directory = BASE_DIR / directory_path
        if not directory.exists():
            return
        for file_path in sorted(directory.glob("*.sql")):
            self.run_file(str(file_path))
