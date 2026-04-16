from __future__ import annotations

import subprocess
import sys

try:
    from _bootstrap import bootstrap_project_root
except ModuleNotFoundError:  # pragma: no cover
    from scripts._bootstrap import bootstrap_project_root


PROJECT_DIR = bootstrap_project_root()


def run_step(*args: str) -> None:
    subprocess.run([sys.executable, *args], check=True, cwd=PROJECT_DIR)


def main() -> None:
    run_step("scripts/run_real_kaggle_pipeline.py")
    run_step("scripts/run_ml_baseline.py")


if __name__ == "__main__":
    main()
