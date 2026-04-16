import pandas as pd


REGION_NORMALIZATION_MAP = {
    "ile de france": "Ile-de-France",
    "ile-de-france": "Ile-de-France",
    "auvergne rhone alpes": "Auvergne-Rhone-Alpes",
    "auvergne-rhone-alpes": "Auvergne-Rhone-Alpes",
    "provence alpes cote d'azur": "Provence-Alpes-Cote d'Azur",
    "provence-alpes-cote-d-azur": "Provence-Alpes-Cote d'Azur",
    "hauts de france": "Hauts-de-France",
    "hauts-de-france": "Hauts-de-France",
    "bourgogne franche comte": "Bourgogne-Franche-Comte",
    "bourgogne-franche-comte": "Bourgogne-Franche-Comte",
    "centre val de loire": "Centre-Val-de-Loire",
    "centre-val-de-loire": "Centre-Val-de-Loire",
    "grand est": "Grand Est",
    "grand-est": "Grand Est",
    "nouvelle aquitaine": "Nouvelle-Aquitaine",
    "nouvelle-aquitaine": "Nouvelle-Aquitaine",
    "pays de la loire": "Pays de la Loire",
    "pays-de-la-loire": "Pays de la Loire",
}

REGION_CODE_MAP = {
    "11": "Ile-de-France",
    "24": "Centre-Val-de-Loire",
    "27": "Bourgogne-Franche-Comte",
    "28": "Normandie",
    "32": "Hauts-de-France",
    "44": "Grand Est",
    "52": "Pays de la Loire",
    "53": "Bretagne",
    "75": "Nouvelle-Aquitaine",
    "76": "Occitanie",
    "84": "Auvergne-Rhone-Alpes",
    "93": "Provence-Alpes-Cote d'Azur",
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

    def normalize_region(value: object) -> object:
        if pd.isna(value):
            return value

        raw_value = str(value).strip()
        lowered = raw_value.lower()
        if lowered in REGION_NORMALIZATION_MAP:
            return REGION_NORMALIZATION_MAP[lowered]

        normalized_code = lowered.removesuffix(".0")
        if normalized_code in REGION_CODE_MAP:
            return REGION_CODE_MAP[normalized_code]

        return raw_value

    normalized[column_name] = series.apply(normalize_region)
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

    if not renamed.columns.duplicated().any():
        return renamed

    consolidated_columns: dict[str, pd.Series] = {}
    for column in dict.fromkeys(renamed.columns):
        matching_columns = renamed.loc[:, renamed.columns == column]
        if matching_columns.shape[1] == 1:
            consolidated_columns[column] = matching_columns.iloc[:, 0]
            continue
        consolidated_columns[column] = matching_columns.bfill(axis=1).iloc[:, 0]

    return pd.DataFrame(consolidated_columns)
