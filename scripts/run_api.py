from _bootstrap import bootstrap_project_root

bootstrap_project_root()

import argparse

import uvicorn

from app.core.config import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the FastAPI service locally.")
    parser.add_argument("--host", help="Optional host override for the local API.")
    parser.add_argument("--port", type=int, help="Optional port override for the local API.")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable hot reload for development. Disabled by default for a more stable demo.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    uvicorn.run(
        "app.api.main:app",
        host=args.host or settings.app_host,
        port=args.port or settings.app_port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
