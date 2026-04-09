import pandas as pd


def add_dju_columns(
    df: pd.DataFrame,
    temp_mean_col: str = "temperature_mean",
    temp_min_col: str = "temperature_min",
    temp_max_col: str = "temperature_max",
    heating_base: float = 18.0,
    cooling_base: float = 24.0,
) -> pd.DataFrame:
    enriched = df.copy()

    if temp_mean_col not in enriched.columns and temp_min_col in enriched.columns and temp_max_col in enriched.columns:
        enriched[temp_mean_col] = (enriched[temp_min_col] + enriched[temp_max_col]) / 2

    if temp_mean_col not in enriched.columns:
        return enriched

    temp_mean = pd.to_numeric(enriched[temp_mean_col], errors="coerce")
    enriched["dju_heating"] = (heating_base - temp_mean).clip(lower=0)
    enriched["dju_cooling"] = (temp_mean - cooling_base).clip(lower=0)
    return enriched
