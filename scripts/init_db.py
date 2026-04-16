from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse

from app.core.logger import setup_logging
from app.db.connection import get_sqlite_database_path
from app.db.sql_runner import SQLRunner


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize the SQLite schema used by the demo.")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete the existing SQLite database before recreating the schema.",
    )
    return parser.parse_args()



def main() -> None:
    args = parse_args()
    setup_logging()
    db_path = get_sqlite_database_path()
    if args.reset and db_path.exists():
        try:
            db_path.unlink()
        except PermissionError as exc:
            raise SystemExit(
                "SQLite database is locked. Stop `python scripts/run_api.py`, close Swagger or any SQLite viewer, "
                "then retry `python scripts/init_db.py --reset`."
            ) from exc
        print(f"Existing database deleted: {db_path}")
    runner = SQLRunner()
    runner.run_directory("sql/ddl")
    runner.run_directory("sql/views")
    print("Database initialization completed (DDL + views).")


if __name__ == "__main__":
    main()
