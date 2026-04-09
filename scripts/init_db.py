from _bootstrap import bootstrap_project_root

bootstrap_project_root()

from app.core.logger import setup_logging
from app.db.sql_runner import SQLRunner



def main() -> None:
    setup_logging()
    runner = SQLRunner()
    runner.run_directory("sql/ddl")
    runner.run_directory("sql/views")
    print("Database initialization completed (DDL + views).")


if __name__ == "__main__":
    main()
