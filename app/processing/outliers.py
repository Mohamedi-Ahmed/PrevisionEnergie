from dataclasses import dataclass, field

import pandas as pd


@dataclass(slots=True)
class OutlierReport:
    total_clipped_values: int = 0
    clipped_by_column: dict[str, int] = field(default_factory=dict)



def clip_outliers_iqr(df: pd.DataFrame, numeric_columns: list[str]) -> tuple[pd.DataFrame, OutlierReport]:
    clipped = df.copy()
    report = OutlierReport()

    for column in numeric_columns:
        if column not in clipped.columns:
            continue
        series = clipped[column]
        if series.isna().all():
            continue
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        if pd.isna(iqr) or iqr == 0:
            continue
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        below_mask = series < lower_bound
        above_mask = series > upper_bound
        clipped_count = int(below_mask.sum() + above_mask.sum())
        if clipped_count == 0:
            continue
        clipped[column] = series.clip(lower=lower_bound, upper=upper_bound)
        report.total_clipped_values += clipped_count
        report.clipped_by_column[column] = clipped_count

    return clipped, report
