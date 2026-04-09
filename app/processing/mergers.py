import pandas as pd


def left_merge(df_left: pd.DataFrame, df_right: pd.DataFrame, on: list[str]) -> pd.DataFrame:
    return df_left.merge(df_right, how="left", on=on)
