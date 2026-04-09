import pandas as pd


def empty_dataframe(columns: list[str] | None = None) -> pd.DataFrame:
    return pd.DataFrame(columns=columns or [])
