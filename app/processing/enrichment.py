from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd

from app.core.logger import get_logger
from app.processing.cleaners import (
    cast_date_column,
    cast_numeric_columns,
    drop_empty_rows,
    standardize_column_names,
    strip_string_values,
)
from app.processing.normalizers import apply_column_aliases, normalize_region_values
from app.processing.schemas import get_schema_profile
from app.storage.base import StorageBackend


logger = get_logger(__name__)


class KaggleAPIEnricher:
    """Enriches the Kaggle dataframe with auxiliary API datasets when available.

    Strategy:
    - Kaggle remains the master dataset.
    - API sources are optional.
    - matching is performed on (date, region)
    - overlapping numeric fields can fill missing Kaggle values
    - new columns from API sources can be appended if they do not exist yet
    """

    def __init__(self, storage_backend: StorageBackend) -> None:
        self.storage_backend = storage_backend
        self.api_sources = ["rte", "meteo_france", "data_gouv"]
        self.schema_profile = get_schema_profile("kaggle")
        self.join_keys = ["date", "region"]
        self.numeric_candidates = set(self.schema_profile.numeric_columns)

    def enrich(self, kaggle_df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
        enriched = kaggle_df.copy()
        enriched = standardize_column_names(enriched)
        enriched = apply_column_aliases(enriched, self.schema_profile.column_aliases)
        enriched = strip_string_values(enriched)
        enriched = cast_date_column(enriched, self.schema_profile.date_column)
        enriched = cast_numeric_columns(enriched, self.schema_profile.numeric_columns)
        enriched = normalize_region_values(enriched, column_name="region")
        if "date" in enriched.columns:
            enriched["date"] = pd.to_datetime(enriched["date"], errors="coerce").dt.normalize()

        report: dict[str, Any] = {
            "api_sources_detected": [],
            "api_sources_merged": [],
            "filled_values_by_source": {},
            "added_columns": [],
        }

        for source_name in self.api_sources:
            auxiliary_df = self._load_latest_auxiliary_dataset(source_name)
            if auxiliary_df is None or auxiliary_df.empty:
                continue

            report["api_sources_detected"].append(source_name)
            auxiliary_df = self._prepare_auxiliary_dataframe(auxiliary_df)
            if auxiliary_df.empty or not all(key in auxiliary_df.columns for key in self.join_keys):
                logger.warning(
                    "Skipping enrichment source=%s because join keys are missing or dataset is empty.",
                    source_name,
                )
                continue

            enriched, source_report = self._merge_source(enriched, auxiliary_df, source_name)
            report["api_sources_merged"].append(source_name)
            report["filled_values_by_source"][source_name] = source_report["filled_values"]
            report["added_columns"].extend(source_report["added_columns"])

        report["added_columns"] = sorted(set(report["added_columns"]))
        return enriched, report

    def _load_latest_auxiliary_dataset(self, source_name: str) -> pd.DataFrame | None:
        bronze_dir = f"bronze/{source_name}"
        files = [path for path in self.storage_backend.list_files(bronze_dir) if path.endswith((".csv", ".json"))]
        if not files:
            return None

        latest_file = sorted(files)[-1]
        content = self.storage_backend.read_bytes(latest_file)
        suffix = Path(latest_file).suffix.lower()

        logger.info("Loading auxiliary source=%s file=%s for Kaggle enrichment", source_name, latest_file)

        if suffix == ".csv":
            return pd.read_csv(StringIO(content.decode("utf-8")))

        if suffix == ".json":
            payload = json.loads(content.decode("utf-8"))
            if isinstance(payload, list):
                return pd.json_normalize(payload)
            if isinstance(payload, dict):
                return pd.json_normalize(payload)

        return None

    def _prepare_auxiliary_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        prepared = standardize_column_names(df)
        prepared = apply_column_aliases(prepared, self.schema_profile.column_aliases)
        prepared = strip_string_values(prepared)
        prepared = drop_empty_rows(prepared)
        prepared = cast_date_column(prepared, self.schema_profile.date_column)
        prepared = cast_numeric_columns(prepared, self.schema_profile.numeric_columns)
        prepared = normalize_region_values(prepared, column_name="region")

        if "date" in prepared.columns:
            prepared["date"] = pd.to_datetime(prepared["date"], errors="coerce").dt.normalize()

        # reduce duplicates on join keys by keeping mean for numeric columns and first for others
        if all(key in prepared.columns for key in self.join_keys):
            numeric_cols = [col for col in prepared.columns if col in self.numeric_candidates]
            other_cols = [col for col in prepared.columns if col not in self.join_keys + numeric_cols]
            aggregations = {col: "mean" for col in numeric_cols}
            aggregations.update({col: "first" for col in other_cols})
            prepared = prepared.groupby(self.join_keys, as_index=False).agg(aggregations)

        return prepared

    def _merge_source(self, base_df: pd.DataFrame, auxiliary_df: pd.DataFrame, source_name: str) -> tuple[pd.DataFrame, dict[str, Any]]:
        result = base_df.copy()
        if "date" in result.columns:
            result["date"] = pd.to_datetime(result["date"], errors="coerce").dt.normalize()

        overlap_columns = [
            col for col in auxiliary_df.columns if col in result.columns and col not in self.join_keys
        ]
        new_columns = [
            col for col in auxiliary_df.columns if col not in result.columns and col not in self.join_keys
        ]

        suffix_map = {col: f"{col}__{source_name}" for col in overlap_columns}
        auxiliary_renamed = auxiliary_df.rename(columns=suffix_map)
        merged = result.merge(auxiliary_renamed, how="left", on=self.join_keys)

        filled_values: dict[str, int] = {}
        for column in overlap_columns:
            aux_col = suffix_map[column]
            if column in self.numeric_candidates:
                missing_mask = merged[column].isna() & merged[aux_col].notna()
                filled_values[column] = int(missing_mask.sum())
                merged[column] = merged[column].fillna(merged[aux_col])
            merged = merged.drop(columns=[aux_col])

        added_columns = []
        for column in new_columns:
            added_columns.append(column)

        return merged, {
            "filled_values": filled_values,
            "added_columns": added_columns,
        }
