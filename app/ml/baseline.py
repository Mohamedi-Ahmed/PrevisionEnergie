from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sqlite3

import numpy as np
import pandas as pd


TARGET_CONFIG = {
    "electricity_consumption": {
        "lag_1": "electricity_lag_1",
        "lag_7": "electricity_lag_7",
        "avg_7d": "electricity_avg_7d",
        "avg_30d": "electricity_avg_30d",
    },
    "gas_consumption": {
        "lag_1": "gas_lag_1",
        "lag_7": "gas_lag_7",
        "avg_7d": "gas_avg_7d",
        "avg_30d": "gas_avg_30d",
    },
}


@dataclass(slots=True)
class BaselineArtifacts:
    summary: dict[str, object]
    predictions: pd.DataFrame


def load_gold_features(db_path: Path) -> pd.DataFrame:
    with sqlite3.connect(db_path) as connection:
        df = pd.read_sql_query(
            """
            SELECT
                feature_date,
                region,
                electricity_consumption,
                gas_consumption,
                temperature_mean,
                temperature_min,
                temperature_max,
                humidity,
                wind_speed,
                precipitation,
                dju_heating,
                dju_cooling,
                is_weekend,
                month,
                year,
                electricity_lag_1,
                electricity_lag_7,
                gas_lag_1,
                gas_lag_7,
                electricity_avg_7d,
                electricity_avg_30d,
                gas_avg_7d,
                gas_avg_30d,
                temperature_avg_7d,
                dju_heating_sum_7d,
                dju_heating_sum_30d,
                precipitation_sum_7d,
                precipitation_sum_30d
            FROM gold_daily_features
            ORDER BY feature_date, region
            """,
            connection,
        )
    if df.empty:
        return df

    df["feature_date"] = pd.to_datetime(df["feature_date"], errors="coerce")
    if "temperature_mean" in df.columns:
        missing_mean = df["temperature_mean"].isna()
        can_derive = df["temperature_min"].notna() & df["temperature_max"].notna()
        df.loc[missing_mean & can_derive, "temperature_mean"] = (
            df.loc[missing_mean & can_derive, "temperature_min"]
            + df.loc[missing_mean & can_derive, "temperature_max"]
        ) / 2
    return df


def _compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    ss_res = float(np.sum((y_true - y_pred) ** 2))
    ss_tot = float(np.sum((y_true - np.mean(y_true)) ** 2))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return {"mae": mae, "rmse": rmse, "r2": r2}


def _time_split(df: pd.DataFrame, test_ratio: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame]:
    unique_dates = sorted(df["feature_date"].dropna().unique())
    if len(unique_dates) < 10:
        raise ValueError("Not enough distinct dates to compute a meaningful time-based split.")

    split_index = max(1, int(len(unique_dates) * (1 - test_ratio)))
    split_index = min(split_index, len(unique_dates) - 1)
    split_date = unique_dates[split_index]
    train_df = df[df["feature_date"] < split_date].copy()
    test_df = df[df["feature_date"] >= split_date].copy()
    if train_df.empty or test_df.empty:
        raise ValueError("Time split produced an empty train or test dataset.")
    return train_df, test_df


def _build_feature_frame(df: pd.DataFrame, target_column: str) -> tuple[pd.DataFrame, list[str]]:
    target_cfg = TARGET_CONFIG[target_column]
    working = df.copy()
    working["feature_date"] = pd.to_datetime(working["feature_date"], errors="coerce")
    feature_columns = [
        target_cfg["lag_1"],
        target_cfg["lag_7"],
        target_cfg["avg_7d"],
        target_cfg["avg_30d"],
        "temperature_mean",
        "precipitation",
        "dju_heating",
        "is_weekend",
        "month",
    ]
    existing_columns = [column for column in feature_columns if column in working.columns]
    required_columns = ["feature_date", "region", target_column, *existing_columns]
    working = working[required_columns].dropna(subset=[target_column, target_cfg["lag_1"]]).copy()
    if working.empty:
        raise ValueError(f"No usable rows found for target={target_column}.")

    categorical = pd.get_dummies(working["region"], prefix="region", dtype=float)
    numeric = working[existing_columns].apply(pd.to_numeric, errors="coerce")
    numeric = numeric[[column for column in numeric.columns if numeric[column].notna().any()]]
    numeric = numeric.fillna(numeric.median(numeric_only=True))
    numeric = numeric.fillna(0.0)
    feature_frame = pd.concat(
        [
            working[["feature_date", "region", target_column]].reset_index(drop=True),
            numeric.reset_index(drop=True),
            categorical.reset_index(drop=True),
        ],
        axis=1,
    )
    model_columns = [column for column in feature_frame.columns if column not in {"feature_date", "region", target_column}]
    return feature_frame, model_columns


def run_baseline_for_target(df: pd.DataFrame, target_column: str, test_ratio: float = 0.2) -> BaselineArtifacts:
    if target_column not in TARGET_CONFIG:
        raise ValueError(f"Unsupported target column: {target_column}")

    feature_frame, model_columns = _build_feature_frame(df, target_column)
    train_df, test_df = _time_split(feature_frame, test_ratio=test_ratio)

    target_cfg = TARGET_CONFIG[target_column]
    baseline_column = target_cfg["lag_1"]

    y_train = train_df[target_column].to_numpy(dtype=float)
    y_test = test_df[target_column].to_numpy(dtype=float)

    x_train = train_df[model_columns].to_numpy(dtype=float)
    x_test = test_df[model_columns].to_numpy(dtype=float)
    x_train = np.column_stack([np.ones(len(x_train)), x_train])
    x_test = np.column_stack([np.ones(len(x_test)), x_test])

    coefficients = np.linalg.pinv(x_train) @ y_train
    linear_predictions = x_test @ coefficients
    linear_predictions = np.clip(linear_predictions, a_min=0.0, a_max=None)

    naive_predictions = test_df[baseline_column].to_numpy(dtype=float)

    predictions = test_df[["feature_date", "region"]].copy()
    predictions["target"] = target_column
    predictions["actual_value"] = test_df[target_column].to_numpy(dtype=float)
    predictions["naive_prediction"] = naive_predictions
    predictions["linear_prediction"] = linear_predictions
    predictions["absolute_error_naive"] = np.abs(predictions["actual_value"] - predictions["naive_prediction"])
    predictions["absolute_error_linear"] = np.abs(predictions["actual_value"] - predictions["linear_prediction"])

    summary = {
        "target": target_column,
        "row_count_total": int(len(feature_frame)),
        "row_count_train": int(len(train_df)),
        "row_count_test": int(len(test_df)),
        "train_start": train_df["feature_date"].min().strftime("%Y-%m-%d"),
        "train_end": train_df["feature_date"].max().strftime("%Y-%m-%d"),
        "test_start": test_df["feature_date"].min().strftime("%Y-%m-%d"),
        "test_end": test_df["feature_date"].max().strftime("%Y-%m-%d"),
        "features_used": model_columns,
        "naive_lag_1_metrics": _compute_metrics(y_test, naive_predictions),
        "linear_regression_metrics": _compute_metrics(y_test, linear_predictions),
    }
    return BaselineArtifacts(summary=summary, predictions=predictions)
