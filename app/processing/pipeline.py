import json
from pathlib import Path

import pandas as pd

from app.core.logger import get_logger
from app.processing.calendar_features import add_basic_calendar_features
from app.processing.cleaners import (
    cast_date_column,
    cast_numeric_columns,
    drop_empty_rows,
    standardize_column_names,
    strip_string_values,
)
from app.processing.dju import add_dju_columns
from app.processing.enrichment import KaggleAPIEnricher
from app.processing.imputers import simple_impute
from app.processing.normalizers import apply_column_aliases, normalize_region_values
from app.processing.outliers import clip_outliers_iqr
from app.processing.quality import QualityReport, compute_missing_counts
from app.processing.schemas import get_schema_profile
from app.processing.validators import validate_not_empty, validate_required_columns
from app.storage.base import StorageBackend


logger = get_logger(__name__)


class BronzeToSilverProcessor:
    def __init__(self, storage_backend: StorageBackend, source_name: str, enrich_from_api: bool = False) -> None:
        self.storage_backend = storage_backend
        self.source_name = source_name
        self.enrich_from_api = enrich_from_api
        self.schema_profile = get_schema_profile(source_name)

    def process_file(self, bronze_relative_path: str, silver_relative_dir: str | None = None) -> tuple[str, str | None, QualityReport]:
        silver_relative_dir = silver_relative_dir or f"silver/{self.source_name}"
        df_raw = self._read_bronze_file(bronze_relative_path)
        validate_not_empty(df_raw, dataset_name=bronze_relative_path)

        rows_initial = len(df_raw)
        missing_before = compute_missing_counts(df_raw)

        df = standardize_column_names(df_raw)
        df = apply_column_aliases(df, self.schema_profile.column_aliases)
        validate_required_columns(df, self.schema_profile.required_columns)
        df = strip_string_values(df)
        df = drop_empty_rows(df)
        rows_after_drop_empty = len(df)

        df = cast_date_column(df, self.schema_profile.date_column)
        df = cast_numeric_columns(df, self.schema_profile.numeric_columns)
        df = self._derive_temperature_mean(df)
        df = normalize_region_values(df, column_name="region")

        if self.source_name == "kaggle" and self.enrich_from_api:
            enricher = KaggleAPIEnricher(storage_backend=self.storage_backend)
            df, enrichment_report = enricher.enrich(df)
            logger.info("Kaggle enrichment applied | report=%s", enrichment_report)

        duplicates_before = len(df)
        key_columns = [column for column in self.schema_profile.key_columns if column in df.columns]
        if key_columns:
            df = df.drop_duplicates(subset=key_columns, keep="first")
        else:
            df = df.drop_duplicates(keep="first")
        rows_after_deduplication = len(df)
        duplicates_removed = duplicates_before - rows_after_deduplication

        df, imputation_report = simple_impute(
            df,
            numeric_columns=[column for column in self.schema_profile.numeric_columns if column in df.columns],
            categorical_columns=[column for column in self.schema_profile.categorical_columns if column in df.columns],
        )

        df, outlier_report = clip_outliers_iqr(
            df,
            numeric_columns=[column for column in self.schema_profile.numeric_columns if column in df.columns],
        )

        df = add_dju_columns(
            df,
            heating_base=self.schema_profile.dju_heating_base,
            cooling_base=self.schema_profile.dju_cooling_base,
        )
        df = add_basic_calendar_features(df, self.schema_profile.date_column)

        missing_after = compute_missing_counts(df)
        quality_report = QualityReport(
            source_name=self.source_name,
            rows_initial=rows_initial,
            rows_after_drop_empty=rows_after_drop_empty,
            rows_after_deduplication=rows_after_deduplication,
            duplicates_removed=duplicates_removed,
            missing_before=missing_before,
            missing_after=missing_after,
            imputed_by_column=imputation_report.imputed_by_column,
            outliers_clipped_by_column=outlier_report.clipped_by_column,
            dtypes_after={column: str(dtype) for column, dtype in df.dtypes.to_dict().items()},
        )

        silver_relative_path = self._write_silver_file(df=df, bronze_relative_path=bronze_relative_path, silver_relative_dir=silver_relative_dir)
        quality_relative_path = self._write_quality_report(
            quality_report=quality_report,
            bronze_relative_path=bronze_relative_path,
            silver_relative_dir=silver_relative_dir,
        )

        self._log_quality(quality_report)
        return silver_relative_path, quality_relative_path, quality_report

    @staticmethod
    def _derive_temperature_mean(df: pd.DataFrame) -> pd.DataFrame:
        enriched = df.copy()
        if "temperature_mean" not in enriched.columns:
            enriched["temperature_mean"] = None
        if "temperature_min" not in enriched.columns or "temperature_max" not in enriched.columns:
            return enriched

        missing_mean = enriched["temperature_mean"].isna()
        has_min_max = enriched["temperature_min"].notna() & enriched["temperature_max"].notna()
        enriched.loc[missing_mean & has_min_max, "temperature_mean"] = (
            enriched.loc[missing_mean & has_min_max, "temperature_min"]
            + enriched.loc[missing_mean & has_min_max, "temperature_max"]
        ) / 2
        return enriched

    def _read_bronze_file(self, bronze_relative_path: str) -> pd.DataFrame:
        content = self.storage_backend.read_bytes(bronze_relative_path)
        suffix = Path(bronze_relative_path).suffix.lower()

        if suffix == ".csv":
            from io import StringIO
            return pd.read_csv(StringIO(content.decode("utf-8")))

        if suffix == ".json":
            payload = json.loads(content.decode("utf-8"))
            if isinstance(payload, list):
                return pd.json_normalize(payload)
            if isinstance(payload, dict):
                return pd.json_normalize(payload)
            raise ValueError(f"Unsupported JSON payload structure in {bronze_relative_path}")

        raise ValueError(f"Unsupported bronze file format: {suffix}")

    def _write_silver_file(self, df: pd.DataFrame, bronze_relative_path: str, silver_relative_dir: str) -> str:
        output_filename = f"silver_{Path(bronze_relative_path).stem}.csv"
        silver_relative_path = f"{silver_relative_dir}/{output_filename}"
        csv_content = df.to_csv(index=False).encode("utf-8")
        self.storage_backend.write_bytes(silver_relative_path, csv_content)
        return silver_relative_path

    def _write_quality_report(self, quality_report: QualityReport, bronze_relative_path: str, silver_relative_dir: str) -> str:
        quality_dir = f"{silver_relative_dir}/quality_reports"
        output_filename = f"quality_{Path(bronze_relative_path).stem}.json"
        quality_relative_path = f"{quality_dir}/{output_filename}"
        content = json.dumps(quality_report.to_dict(), ensure_ascii=False, indent=2).encode("utf-8")
        self.storage_backend.write_bytes(quality_relative_path, content)
        return quality_relative_path

    def _log_quality(self, report: QualityReport) -> None:
        logger.info(
            (
                "Silver quality | source=%s | rows_initial=%s | rows_after_drop_empty=%s | "
                "rows_after_deduplication=%s | duplicates_removed=%s | total_imputed=%s | total_outliers_clipped=%s"
            ),
            report.source_name,
            report.rows_initial,
            report.rows_after_drop_empty,
            report.rows_after_deduplication,
            report.duplicates_removed,
            sum(report.imputed_by_column.values()),
            sum(report.outliers_clipped_by_column.values()),
        )
