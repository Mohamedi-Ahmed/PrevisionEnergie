import pandas as pd


CORE_IDENTIFIER_COLUMNS = {"date", "region"}


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    cleaned.columns = [str(col).strip().lower().replace(" ", "_") for col in cleaned.columns]
    return cleaned


def strip_string_values(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()
    object_columns = cleaned.select_dtypes(include=["object", "string"]).columns
    for column in object_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()
    return cleaned


def drop_empty_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(how="all").copy()


def cast_numeric_columns(df: pd.DataFrame, numeric_columns: list[str]) -> pd.DataFrame:
    typed = df.copy()
    for column in numeric_columns:
        if column in typed.columns:
            typed[column] = pd.to_numeric(typed[column], errors="coerce")
    return typed


def cast_date_column(df: pd.DataFrame, date_column: str) -> pd.DataFrame:
    typed = df.copy()
    if date_column in typed.columns:
        typed[date_column] = pd.to_datetime(typed[date_column], errors="coerce")
    return typed
