import pandas as pd


REGION_NORMALIZATION_MAP = {
    "ile de france": "Île-de-France",
    "ile-de-france": "Île-de-France",
    "auvergne rhone alpes": "Auvergne-Rhône-Alpes",
    "provence alpes cote d'azur": "Provence-Alpes-Côte d'Azur",
}


def normalize_dates(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    normalized = df.copy()
    if column_name in normalized.columns:
        normalized[column_name] = pd.to_datetime(normalized[column_name], errors="coerce")
    return normalized


def normalize_region_values(df: pd.DataFrame, column_name: str = "region") -> pd.DataFrame:
    normalized = df.copy()
    if column_name not in normalized.columns:
        return normalized

    series = normalized[column_name].astype("string").str.strip()
    canonical_map = {key: value for key, value in REGION_NORMALIZATION_MAP.items()}
    normalized[column_name] = series.apply(
        lambda value: canonical_map.get(str(value).lower(), value) if pd.notna(value) else value
    )
    return normalized


def apply_column_aliases(df: pd.DataFrame, aliases: dict[str, list[str]]) -> pd.DataFrame:
    renamed = df.copy()
    reverse_aliases: dict[str, str] = {}
    for canonical_name, alias_list in aliases.items():
        for alias in alias_list:
            reverse_aliases[alias] = canonical_name

    new_columns = []
    for column in renamed.columns:
        new_columns.append(reverse_aliases.get(column, column))
    renamed.columns = new_columns
    return renamed
