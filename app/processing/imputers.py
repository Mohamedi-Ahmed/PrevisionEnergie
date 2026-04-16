from dataclasses import dataclass, field

import pandas as pd


@dataclass(slots=True)
class ImputationReport:
    total_imputed_values: int = 0
    imputed_by_column: dict[str, int] = field(default_factory=dict)



def simple_impute(df: pd.DataFrame, numeric_columns: list[str], categorical_columns: list[str]) -> tuple[pd.DataFrame, ImputationReport]:
    imputed = df.copy()
    report = ImputationReport()

    for column in numeric_columns:
        if column not in imputed.columns:
            continue
        missing_before = int(imputed[column].isna().sum())
        if missing_before == 0:
            continue
        non_null_values = imputed[column].dropna()
        if non_null_values.empty:
            continue
        median_value = non_null_values.median()
        imputed[column] = imputed[column].fillna(median_value)
        report.total_imputed_values += missing_before
        report.imputed_by_column[column] = missing_before

    for column in categorical_columns:
        if column not in imputed.columns:
            continue
        missing_before = int(imputed[column].isna().sum())
        if missing_before == 0:
            continue
        mode = imputed[column].mode(dropna=True)
        fill_value = mode.iloc[0] if not mode.empty else "unknown"
        imputed[column] = imputed[column].fillna(fill_value)
        report.total_imputed_values += missing_before
        report.imputed_by_column[column] = report.imputed_by_column.get(column, 0) + missing_before

    return imputed, report
