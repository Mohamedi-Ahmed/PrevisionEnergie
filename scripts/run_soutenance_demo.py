from __future__ import annotations

import argparse
import json
import socketserver
import sqlite3
import subprocess
import sys
import threading
from datetime import date, timedelta
from http.server import BaseHTTPRequestHandler
from pathlib import Path

try:
    from _bootstrap import bootstrap_project_root
except ModuleNotFoundError:  # pragma: no cover
    from scripts._bootstrap import bootstrap_project_root


PROJECT_DIR = bootstrap_project_root()

from app.core.config import get_settings
from app.db.connection import get_sqlite_database_path


def build_demo_api_payload() -> list[dict[str, object]]:
    return [
        {
            "date": "2024-01-03",
            "region": "ile de france",
            "electricity_consumption": 130,
            "gas_consumption": 62,
            "temperature_mean": 7.5,
            "temperature_min": 4.0,
            "temperature_max": 10.0,
            "humidity": 72,
            "wind_speed": 18,
            "precipitation": 1.5,
        }
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a stable soutenance demo with Kaggle + API extraction, ETL and summary."
    )
    parser.add_argument(
        "--kaggle-source-file",
        default="data/bronze/kaggle/demo_pipeline.csv",
        help="Local Kaggle CSV used for the demo extraction.",
    )
    parser.add_argument(
        "--api-source",
        default="rte",
        choices=["rte", "meteo_france", "data_gouv"],
        help="API source showcased during the demo.",
    )
    parser.add_argument(
        "--api-mode",
        default="mock",
        choices=["mock", "live"],
        help="Use a local mock API by default, or a live API if an absolute URL is provided.",
    )
    parser.add_argument("--api-absolute-url", help="Absolute URL used when --api-mode live.")
    parser.add_argument("--api-params", default="{}", help="Optional JSON params for the API call.")
    parser.add_argument("--port", type=int, default=8765, help="Port used by the local mock API.")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.api_mode == "live" and not args.api_absolute_url:
        raise SystemExit("Specify --api-absolute-url when using --api-mode live.")


class DemoAPIHandler(BaseHTTPRequestHandler):
    payload = build_demo_api_payload()

    def do_GET(self) -> None:  # pragma: no cover - exercised through the demo script
        content = json.dumps(self.payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def log_message(self, format: str, *args) -> None:  # pragma: no cover
        return


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def build_pipeline_command(args: argparse.Namespace, api_absolute_url: str) -> list[str]:
    return [
        sys.executable,
        "scripts/run_pipeline.py",
        "--kaggle-source-file",
        args.kaggle_source_file,
        "--api-source",
        args.api_source,
        "--api-absolute-url",
        api_absolute_url,
        "--api-params",
        args.api_params,
    ]


def run_pipeline_subprocess(command: list[str]) -> None:
    try:
        subprocess.run(command, check=True, cwd=PROJECT_DIR)
    except subprocess.CalledProcessError as exc:
        raise SystemExit(
            "Soutenance demo preparation failed. "
            "If SQLite is locked, stop the API or any DB viewer, then rerun `python scripts/run_soutenance_demo.py`."
        ) from exc


def query_demo_summary(db_path: Path) -> dict[str, object]:
    connection = sqlite3.connect(db_path)
    summary = {
        "bronze_logs": connection.execute("SELECT COUNT(*) FROM bronze_ingestion_log").fetchone()[0],
        "silver_rows": connection.execute("SELECT COUNT(*) FROM silver_energy_weather_daily").fetchone()[0],
        "gold_rows": connection.execute("SELECT COUNT(*) FROM gold_daily_features").fetchone()[0],
        "latest_bronze_sources": connection.execute(
            """
            SELECT source_name, storage_path
            FROM bronze_ingestion_log
            ORDER BY ingestion_id DESC
            LIMIT 5
            """
        ).fetchall(),
        "feature_preview": connection.execute(
            """
            SELECT feature_date, region, electricity_lag_1, electricity_avg_7d
            FROM gold_daily_features
            ORDER BY feature_date, region
            LIMIT 5
            """
        ).fetchall(),
        "sample_api_call": connection.execute(
            """
            SELECT feature_date, region
            FROM gold_daily_features
            ORDER BY feature_date, region
            LIMIT 1
            """
        ).fetchone(),
    }
    connection.close()
    return summary


def print_demo_summary(api_absolute_url: str) -> None:
    settings = get_settings()
    db_path = get_sqlite_database_path()
    summary = query_demo_summary(db_path)

    print("Demo summary")
    print(f"API source shown: {api_absolute_url}")
    print(f"Bronze log rows: {summary['bronze_logs']}")
    print(f"Silver rows: {summary['silver_rows']}")
    print(f"Gold rows: {summary['gold_rows']}")
    print("Latest Bronze sources:")
    for source_name, storage_path in summary["latest_bronze_sources"]:
        print(f"- {source_name}: {storage_path}")
    print("Feature preview:")
    for feature_date, region, electricity_lag_1, electricity_avg_7d in summary["feature_preview"]:
        print(
            f"- {feature_date} | {region} | lag_1={electricity_lag_1} | avg_7d={electricity_avg_7d}"
        )
    sample_api_call = summary["sample_api_call"]
    if sample_api_call is not None:
        sample_date, sample_region = sample_api_call
        start_date = date.fromisoformat(sample_date)
        end_date = start_date + timedelta(days=2)
        print("Suggested API request:")
        print(
            "- GET "
            f"/api/v1/features?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
            f"&region={sample_region}"
        )
        print("Auth flow:")
        print("- POST /api/v1/auth/token")
        print("- then paste the returned bearer token into Swagger Authorize")
    print("Next live step:")
    print(f"- launch API: {sys.executable} scripts/run_api.py")
    print(f"- Swagger: http://127.0.0.1:{settings.app_port}/docs")
    print(f"- Auth user: {settings.api_auth_username}")


def main() -> None:
    args = parse_args()
    validate_args(args)

    if args.api_mode == "live":
        run_pipeline_subprocess(build_pipeline_command(args, args.api_absolute_url))
        print_demo_summary(args.api_absolute_url)
        return

    try:
        server = ReusableTCPServer(("127.0.0.1", args.port), DemoAPIHandler)
    except OSError:
        server = ReusableTCPServer(("127.0.0.1", 0), DemoAPIHandler)

    with server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        actual_port = server.server_address[1]
        if actual_port != args.port:
            print(
                f"Requested mock API port {args.port} was busy. "
                f"Using fallback port {actual_port}."
            )
        api_absolute_url = f"http://127.0.0.1:{actual_port}/demo"
        try:
            run_pipeline_subprocess(build_pipeline_command(args, api_absolute_url))
            print_demo_summary(api_absolute_url)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
