from dataclasses import asdict, dataclass, field

import pandas as pd


@dataclass(slots=True)
class QualityReport:
    source_name: str
    rows_initial: int
    rows_after_drop_empty: int
    rows_after_deduplication: int
    duplicates_removed: int
    missing_before: dict[str, int] = field(default_factory=dict)
    missing_after: dict[str, int] = field(default_factory=dict)
    imputed_by_column: dict[str, int] = field(default_factory=dict)
    outliers_clipped_by_column: dict[str, int] = field(default_factory=dict)
    dtypes_after: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)



def compute_missing_counts(df: pd.DataFrame) -> dict[str, int]:
    return {column: int(count) for column, count in df.isna().sum().to_dict().items()}
