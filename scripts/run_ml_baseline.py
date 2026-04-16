from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

try:
    from _bootstrap import bootstrap_project_root
except ModuleNotFoundError:  # pragma: no cover
    from scripts._bootstrap import bootstrap_project_root


PROJECT_DIR = bootstrap_project_root()

from app.ml.baseline import load_gold_features, run_baseline_for_target


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run a lightweight ML baseline on gold_daily_features and export metrics."
    )
    parser.add_argument(
        "--db-path",
        default=str(PROJECT_DIR / "prevision_energie.db"),
        help="SQLite database used by the project.",
    )
    parser.add_argument(
        "--export-dir",
        default=str(PROJECT_DIR / "data" / "gold" / "exports"),
        help="Directory where metrics and predictions are exported.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    db_path = Path(args.db_path)
    export_dir = Path(args.export_dir)
    export_dir.mkdir(parents=True, exist_ok=True)

    df = load_gold_features(db_path)
    if df.empty:
        raise SystemExit("gold_daily_features is empty. Run the pipeline before the ML baseline.")

    summaries = {}
    prediction_frames = []
    for target in ["electricity_consumption", "gas_consumption"]:
        artifacts = run_baseline_for_target(df, target_column=target)
        summaries[target] = artifacts.summary
        prediction_frames.append(artifacts.predictions)

    predictions_df = pd.concat(prediction_frames, ignore_index=True)

    metrics_path = export_dir / "ml_metrics.json"
    predictions_path = export_dir / "ml_predictions.csv"

    metrics_path.write_text(json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8")
    predictions_df.to_csv(predictions_path, index=False)

    print("=== ML baseline completed ===")
    print(f"Metrics file: {metrics_path}")
    print(f"Predictions file: {predictions_path}")
    for target, summary in summaries.items():
        linear = summary["linear_regression_metrics"]
        naive = summary["naive_lag_1_metrics"]
        print(f"[{target}] rows={summary['row_count_total']} train={summary['row_count_train']} test={summary['row_count_test']}")
        print(f"  naive_lag_1 -> R2={naive['r2']:.4f} | MAE={naive['mae']:.2f} | RMSE={naive['rmse']:.2f}")
        print(f"  linear_regression -> R2={linear['r2']:.4f} | MAE={linear['mae']:.2f} | RMSE={linear['rmse']:.2f}")


if __name__ == "__main__":
    main()
