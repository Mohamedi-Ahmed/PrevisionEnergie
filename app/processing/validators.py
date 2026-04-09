import pandas as pd


def validate_not_empty(df: pd.DataFrame, dataset_name: str) -> None:
    if df.empty:
        raise ValueError(f"Dataset '{dataset_name}' is empty.")


def validate_required_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    missing = [column for column in required_columns if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
