import pandas as pd

from app.ml.baseline import run_baseline_for_target


def _build_dataset() -> pd.DataFrame:
    rows = []
    for day in range(1, 31):
        rows.append(
            {
                "feature_date": f"2024-01-{day:02d}",
                "region": "Ile-de-France" if day % 2 == 0 else "Occitanie",
                "electricity_consumption": 100 + day * 2,
                "gas_consumption": 80 + day,
                "temperature_mean": 5 + day * 0.1,
                "temperature_min": 2 + day * 0.1,
                "temperature_max": 8 + day * 0.1,
                "precipitation": float(day % 3),
                "dju_heating": 15 - day * 0.1,
                "is_weekend": int(day % 7 in {0, 6}),
                "month": 1,
                "electricity_lag_1": 98 + (day - 1) * 2,
                "electricity_lag_7": 90 + max(day - 7, 0) * 2,
                "electricity_avg_7d": 99 + day * 2,
                "electricity_avg_30d": 100 + day * 1.5,
                "gas_lag_1": 79 + (day - 1),
                "gas_lag_7": 72 + max(day - 7, 0),
                "gas_avg_7d": 79 + day,
                "gas_avg_30d": 80 + day * 0.8,
            }
        )
    return pd.DataFrame(rows)


def test_run_baseline_for_target_returns_metrics_and_predictions() -> None:
    df = _build_dataset()
    artifacts = run_baseline_for_target(df, target_column="electricity_consumption", test_ratio=0.2)

    assert artifacts.summary["row_count_total"] > 0
    assert artifacts.summary["row_count_train"] > 0
    assert artifacts.summary["row_count_test"] > 0
    assert "naive_lag_1_metrics" in artifacts.summary
    assert "linear_regression_metrics" in artifacts.summary
    assert not artifacts.predictions.empty
    assert {"naive_prediction", "linear_prediction"}.issubset(artifacts.predictions.columns)
