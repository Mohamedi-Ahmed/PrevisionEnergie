import pandas as pd


def add_basic_calendar_features(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    enriched = df.copy()
    if date_column not in enriched.columns:
        return enriched

    series = pd.to_datetime(enriched[date_column], errors="coerce")
    enriched["year"] = series.dt.year
    enriched["month"] = series.dt.month
    enriched["weekday"] = series.dt.weekday
    enriched["is_weekend"] = series.dt.weekday >= 5
    return enriched
