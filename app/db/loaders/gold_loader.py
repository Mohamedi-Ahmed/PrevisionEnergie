from __future__ import annotations

import hashlib
import sqlite3
import unicodedata
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from app.core.logger import get_logger
from app.db.connection import get_connection
from app.processing.normalizers import normalize_region_values


logger = get_logger(__name__)


MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}

WEEKDAY_NAMES = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

# Local enrichment used to make the demo dimension easier to read.
# This mapping is not presented as a canonical business referential.
REGION_ENRICHMENT = {
    "auvergne-rhone-alpes": {"macro_region": "South-East", "climate_zone": "continental", "territory_type": "metropolitan"},
    "bourgogne-franche-comte": {"macro_region": "East", "climate_zone": "continental", "territory_type": "metropolitan"},
    "bretagne": {"macro_region": "West", "climate_zone": "oceanic", "territory_type": "metropolitan"},
    "centre-val-de-loire": {"macro_region": "Center", "climate_zone": "temperate", "territory_type": "metropolitan"},
    "corse": {"macro_region": "South-East", "climate_zone": "mediterranean", "territory_type": "metropolitan"},
    "grand-est": {"macro_region": "East", "climate_zone": "continental", "territory_type": "metropolitan"},
    "hauts-de-france": {"macro_region": "North", "climate_zone": "oceanic", "territory_type": "metropolitan"},
    "ile-de-france": {"macro_region": "North", "climate_zone": "temperate", "territory_type": "metropolitan"},
    "normandie": {"macro_region": "North-West", "climate_zone": "oceanic", "territory_type": "metropolitan"},
    "nouvelle-aquitaine": {"macro_region": "South-West", "climate_zone": "oceanic", "territory_type": "metropolitan"},
    "occitanie": {"macro_region": "South", "climate_zone": "mediterranean", "territory_type": "metropolitan"},
    "pays-de-la-loire": {"macro_region": "West", "climate_zone": "oceanic", "territory_type": "metropolitan"},
    "provence-alpes-cote-d-azur": {"macro_region": "South-East", "climate_zone": "mediterranean", "territory_type": "metropolitan"},
    "guadeloupe": {"macro_region": "Overseas", "climate_zone": "tropical", "territory_type": "overseas"},
    "martinique": {"macro_region": "Overseas", "climate_zone": "tropical", "territory_type": "overseas"},
    "guyane": {"macro_region": "Overseas", "climate_zone": "equatorial", "territory_type": "overseas"},
    "la reunion": {"macro_region": "Overseas", "climate_zone": "tropical", "territory_type": "overseas"},
    "mayotte": {"macro_region": "Overseas", "climate_zone": "tropical", "territory_type": "overseas"},
}


@dataclass
class GoldLoadResult:
    dim_date_rows: int
    dim_region_rows: int
    dim_energy_rows: int
    dim_weather_rows: int
    fact_rows: int
    service_rows: int

    def to_dict(self) -> dict[str, int]:
        return {
            "dim_date_rows": self.dim_date_rows,
            "dim_region_rows": self.dim_region_rows,
            "dim_energy_rows": self.dim_energy_rows,
            "dim_weather_rows": self.dim_weather_rows,
            "fact_rows": self.fact_rows,
            "service_rows": self.service_rows,
        }


class SilverToGoldLoader:
    def run(self) -> dict[str, int]:
        silver_df = self._read_silver()
        if silver_df.empty:
            logger.warning("No silver rows found. Gold layer was not rebuilt.")
            return GoldLoadResult(0, 0, 0, 0, 0, 0).to_dict()

        silver_df = self._prepare_silver(silver_df)
        silver_df = self._collapse_to_gold_grain(silver_df)
        date_df = self._build_dim_date(silver_df)
        region_df = self._build_dim_region(silver_df)
        energy_df = self._build_dim_energy()
        weather_df, silver_df = self._build_dim_weather_context(silver_df)
        service_df = self._build_service_dataset(silver_df)

        with get_connection() as connection:
            self._load_dim_date(connection, date_df)
            self._load_dim_region(connection, region_df)
            self._load_dim_energy(connection, energy_df)
            self._load_dim_weather(connection, weather_df)
            fact_df = self._build_fact(connection, silver_df)
            self._validate_fact_dimension_keys(fact_df)
            self._load_fact(connection, fact_df)
            self._merge_service_table(connection, service_df)
            connection.commit()

        result = GoldLoadResult(
            dim_date_rows=len(date_df),
            dim_region_rows=len(region_df),
            dim_energy_rows=len(energy_df),
            dim_weather_rows=len(weather_df),
            fact_rows=len(fact_df),
            service_rows=len(service_df),
        )
        logger.info("Gold loader completed | result=%s", result.to_dict())
        return result.to_dict()

    def _read_silver(self) -> pd.DataFrame:
        query = "SELECT * FROM silver_energy_weather_daily ORDER BY date, region"
        with get_connection() as connection:
            return pd.read_sql_query(query, connection)

    def _prepare_silver(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df[df["date"].notna()].copy()
        df["region"] = df["region"].fillna("Unknown").astype(str).str.strip()
        df = normalize_region_values(df, column_name="region")
        for column in [
            "electricity_consumption",
            "gas_consumption",
            "temperature_mean",
            "temperature_min",
            "temperature_max",
            "humidity",
            "wind_speed",
            "precipitation",
            "dju_heating",
            "dju_cooling",
        ]:
            if column in df.columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")
        return df

    def _collapse_to_gold_grain(self, df: pd.DataFrame) -> pd.DataFrame:
        grouped_keys = ["date", "region"]
        if not df.duplicated(subset=grouped_keys).any():
            return df.sort_values(grouped_keys).reset_index(drop=True)

        logger.info(
            "Collapsing Silver duplicates to Gold grain | input_rows=%s | duplicated_grain_rows=%s",
            len(df),
            int(df.duplicated(subset=grouped_keys, keep=False).sum()),
        )

        aggregations: dict[str, str | callable] = {
            "source_name": self._merge_source_names,
            "is_weekend": "max",
            "month": "max",
            "year": "max",
        }
        for column in [
            "electricity_consumption",
            "gas_consumption",
            "temperature_mean",
            "temperature_min",
            "temperature_max",
            "humidity",
            "wind_speed",
            "precipitation",
            "dju_heating",
            "dju_cooling",
        ]:
            if column in df.columns:
                aggregations[column] = "mean"

        collapsed_df = (
            df.groupby(grouped_keys, as_index=False)
            .agg(aggregations)
            .sort_values(grouped_keys)
            .reset_index(drop=True)
        )
        return collapsed_df

    def _build_dim_date(self, df: pd.DataFrame) -> pd.DataFrame:
        dates = pd.DataFrame({"full_date": sorted(df["date"].dt.normalize().drop_duplicates())})
        dates["date_key"] = dates["full_date"].dt.strftime("%Y%m%d").astype(int)
        dates["day"] = dates["full_date"].dt.day
        dates["month"] = dates["full_date"].dt.month
        dates["month_name"] = dates["month"].map(MONTH_NAMES)
        dates["quarter"] = dates["full_date"].dt.quarter
        dates["year"] = dates["full_date"].dt.year
        dates["week_of_year"] = dates["full_date"].dt.isocalendar().week.astype(int)
        dates["day_of_week"] = dates["full_date"].dt.weekday
        dates["weekday_label"] = dates["day_of_week"].map(WEEKDAY_NAMES)
        dates["is_weekend"] = dates["day_of_week"].isin([5, 6]).astype(int)
        dates["is_holiday"] = 0
        dates["is_school_holiday"] = 0
        dates["season"] = dates["month"].map(self._month_to_season)
        dates["full_date"] = dates["full_date"].dt.strftime("%Y-%m-%d")
        return dates

    def _build_dim_region(self, df: pd.DataFrame) -> pd.DataFrame:
        current_date = datetime.utcnow().isoformat()
        regions = pd.DataFrame({"region_name": df["region"].dropna().astype(str).str.strip()})
        regions["region_code"] = regions["region_name"].map(self._slugify)
        regions = (
            regions.groupby("region_code", as_index=False)["region_name"]
            .agg(self._select_region_name)
        )
        # Keep a few descriptive attributes so dim_region is easy to comment live.
        regions["macro_region"] = regions["region_code"].map(
            lambda key: REGION_ENRICHMENT.get(key, {}).get("macro_region", "Unknown")
        )
        regions["climate_zone"] = regions["region_code"].map(
            lambda key: REGION_ENRICHMENT.get(key, {}).get("climate_zone", "temperate")
        )
        regions["territory_type"] = regions["region_code"].map(
            lambda key: REGION_ENRICHMENT.get(key, {}).get("territory_type", "metropolitan")
        )
        regions["valid_from"] = current_date
        regions["valid_to"] = None
        regions["is_current"] = 1
        regions["attr_hash_md5"] = regions.apply(
            lambda row: self._md5(
                row["region_name"],
                row["macro_region"],
                row["climate_zone"],
                row["territory_type"],
            ),
            axis=1,
        )
        return regions

    def _build_dim_energy(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {"energy_code": "ELEC", "energy_label": "Electricity", "unit": "MWh", "is_active": 1},
                {"energy_code": "GAS", "energy_label": "Gas", "unit": "MWh", "is_active": 1},
            ]
        )

    def _build_dim_weather_context(self, df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        working_df = df.copy()
        working_df["temperature_band"] = working_df["temperature_mean"].apply(self._temperature_band)
        working_df["precipitation_band"] = working_df["precipitation"].apply(self._precipitation_band)
        working_df["wind_band"] = working_df["wind_speed"].apply(self._wind_band)
        working_df["humidity_band"] = working_df["humidity"].apply(self._humidity_band)
        working_df["is_extreme_weather"] = (
            (working_df["temperature_mean"].fillna(0) <= -5)
            | (working_df["temperature_mean"].fillna(0) >= 35)
            | (working_df["precipitation"].fillna(0) >= 20)
            | (working_df["wind_speed"].fillna(0) >= 70)
        ).astype(int)
        working_df["weather_profile_label"] = working_df.apply(
            lambda row: f"{row['temperature_band']} / {row['precipitation_band']} / {row['wind_band']}",
            axis=1,
        )
        working_df["weather_profile_nk"] = working_df.apply(
            lambda row: self._md5(
                row["temperature_band"],
                row["precipitation_band"],
                row["wind_band"],
                row["humidity_band"],
                str(row["is_extreme_weather"]),
            ),
            axis=1,
        )
        weather_df = (
            working_df[
                [
                    "weather_profile_nk",
                    "temperature_band",
                    "precipitation_band",
                    "wind_band",
                    "humidity_band",
                    "weather_profile_label",
                    "is_extreme_weather",
                ]
            ]
            .drop_duplicates()
            .reset_index(drop=True)
        )
        return weather_df, working_df

    def _build_fact(
        self,
        connection: sqlite3.Connection,
        silver_df: pd.DataFrame,
    ) -> pd.DataFrame:
        fact_df = silver_df.melt(
            id_vars=[
                "source_name",
                "date",
                "region",
                "dju_heating",
                "dju_cooling",
                "weather_profile_nk",
            ],
            value_vars=["electricity_consumption", "gas_consumption"],
            var_name="energy_column",
            value_name="consumption_value",
        )
        fact_df = fact_df.dropna(subset=["consumption_value"]).copy()
        fact_df["energy_label"] = fact_df["energy_column"].map(
            {
                "electricity_consumption": "Electricity",
                "gas_consumption": "Gas",
            }
        )
        fact_df["region_code"] = fact_df["region"].map(self._slugify)
        date_lookup = pd.read_sql_query(
            "SELECT date_key, full_date AS date_str FROM dim_date",
            connection,
        )
        fact_df["date_str"] = fact_df["date"].dt.strftime("%Y-%m-%d")
        fact_df = fact_df.merge(date_lookup, on="date_str", how="left")
        region_lookup = pd.read_sql_query(
            "SELECT region_key, region_code FROM dim_region WHERE is_current = 1",
            connection,
        )
        fact_df = fact_df.merge(region_lookup, on="region_code", how="left")
        energy_lookup = pd.read_sql_query(
            "SELECT energy_key, energy_label FROM dim_energy WHERE is_active = 1",
            connection,
        )
        fact_df = fact_df.merge(energy_lookup, on="energy_label", how="left")
        weather_lookup = pd.read_sql_query(
            "SELECT weather_key, weather_profile_nk FROM dim_weather_context",
            connection,
        )
        fact_df = fact_df.merge(weather_lookup, on="weather_profile_nk", how="left")
        fact_df["observation_count"] = 1
        return fact_df[
            [
                "date_key",
                "region_key",
                "energy_key",
                "weather_key",
                "source_name",
                "consumption_value",
                "dju_heating",
                "dju_cooling",
                "observation_count",
            ]
        ]

    @staticmethod
    def _validate_fact_dimension_keys(fact_df: pd.DataFrame) -> None:
        missing_keys = [
            column
            for column in ["date_key", "region_key", "energy_key"]
            if fact_df[column].isna().any()
        ]
        if missing_keys:
            raise ValueError(f"Missing dimension keys in fact build: {missing_keys}")

    def _build_service_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        service_df = df.copy().sort_values(["region", "date"]) 
        service_df["feature_date"] = service_df["date"].dt.strftime("%Y-%m-%d")
        service_df["electricity_lag_1"] = service_df.groupby("region")["electricity_consumption"].shift(1)
        service_df["electricity_lag_7"] = service_df.groupby("region")["electricity_consumption"].shift(7)
        service_df["gas_lag_1"] = service_df.groupby("region")["gas_consumption"].shift(1)
        service_df["gas_lag_7"] = service_df.groupby("region")["gas_consumption"].shift(7)
        service_df["electricity_avg_7d"] = (
            service_df.groupby("region")["electricity_consumption"]
            .transform(lambda series: series.rolling(7, min_periods=1).mean())
        )
        service_df["electricity_avg_30d"] = (
            service_df.groupby("region")["electricity_consumption"]
            .transform(lambda series: series.rolling(30, min_periods=1).mean())
        )
        service_df["gas_avg_7d"] = (
            service_df.groupby("region")["gas_consumption"]
            .transform(lambda series: series.rolling(7, min_periods=1).mean())
        )
        service_df["gas_avg_30d"] = (
            service_df.groupby("region")["gas_consumption"]
            .transform(lambda series: series.rolling(30, min_periods=1).mean())
        )
        service_df["temperature_avg_7d"] = (
            service_df.groupby("region")["temperature_mean"]
            .transform(lambda series: series.rolling(7, min_periods=1).mean())
        )
        service_df["dju_heating_sum_7d"] = (
            service_df.groupby("region")["dju_heating"]
            .transform(lambda series: series.rolling(7, min_periods=1).sum())
        )
        service_df["dju_heating_sum_30d"] = (
            service_df.groupby("region")["dju_heating"]
            .transform(lambda series: series.rolling(30, min_periods=1).sum())
        )
        service_df["precipitation_sum_7d"] = (
            service_df.groupby("region")["precipitation"]
            .transform(lambda series: series.rolling(7, min_periods=1).sum())
        )
        service_df["precipitation_sum_30d"] = (
            service_df.groupby("region")["precipitation"]
            .transform(lambda series: series.rolling(30, min_periods=1).sum())
        )
        columns = [
            "feature_date",
            "region",
            "electricity_consumption",
            "gas_consumption",
            "temperature_mean",
            "temperature_min",
            "temperature_max",
            "humidity",
            "wind_speed",
            "precipitation",
            "dju_heating",
            "dju_cooling",
            "is_weekend",
            "month",
            "year",
            "electricity_lag_1",
            "electricity_lag_7",
            "gas_lag_1",
            "gas_lag_7",
            "electricity_avg_7d",
            "electricity_avg_30d",
            "gas_avg_7d",
            "gas_avg_30d",
            "temperature_avg_7d",
            "dju_heating_sum_7d",
            "dju_heating_sum_30d",
            "precipitation_sum_7d",
            "precipitation_sum_30d",
        ]
        for column in columns:
            if column not in service_df.columns:
                service_df[column] = None
        return service_df[columns]

    def _load_dim_date(self, connection: sqlite3.Connection, df: pd.DataFrame) -> None:
        sql = """
            INSERT INTO dim_date (
                date_key, full_date, day, month, month_name, quarter, year,
                week_of_year, day_of_week, weekday_label, is_weekend,
                is_holiday, is_school_holiday, season, updated_at
            ) VALUES (
                :date_key, :full_date, :day, :month, :month_name, :quarter, :year,
                :week_of_year, :day_of_week, :weekday_label, :is_weekend,
                :is_holiday, :is_school_holiday, :season, CURRENT_TIMESTAMP
            )
            ON CONFLICT(date_key) DO UPDATE SET
                full_date = excluded.full_date,
                day = excluded.day,
                month = excluded.month,
                month_name = excluded.month_name,
                quarter = excluded.quarter,
                year = excluded.year,
                week_of_year = excluded.week_of_year,
                day_of_week = excluded.day_of_week,
                weekday_label = excluded.weekday_label,
                is_weekend = excluded.is_weekend,
                is_holiday = excluded.is_holiday,
                is_school_holiday = excluded.is_school_holiday,
                season = excluded.season,
                updated_at = CURRENT_TIMESTAMP
        """
        connection.executemany(sql, df.to_dict(orient="records"))

    def _load_dim_region(self, connection: sqlite3.Connection, df: pd.DataFrame) -> None:
        existing_df = pd.read_sql_query(
            "SELECT region_key, region_code, attr_hash_md5, valid_from, is_current FROM dim_region",
            connection,
        )
        upserts = []
        for row in df.to_dict(orient="records"):
            current = existing_df[
                (existing_df["region_code"] == row["region_code"]) & (existing_df["is_current"] == 1)
            ]
            if current.empty:
                upserts.append(row)
                continue
            existing_hash = current.iloc[0]["attr_hash_md5"]
            if existing_hash != row["attr_hash_md5"]:
                same_version = existing_df[
                    (existing_df["region_code"] == row["region_code"])
                    & (existing_df["attr_hash_md5"] == row["attr_hash_md5"])
                    & (existing_df["valid_from"] == row["valid_from"])
                ]
                if not same_version.empty:
                    same_version_key = int(same_version.iloc[0]["region_key"])
                    connection.execute(
                        """
                        UPDATE dim_region
                        SET is_current = 0,
                            valid_to = :valid_to,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE region_code = :region_code
                          AND is_current = 1
                          AND region_key <> :region_key
                        """,
                        {
                            "valid_to": row["valid_from"],
                            "region_code": row["region_code"],
                            "region_key": same_version_key,
                        },
                    )
                    connection.execute(
                        """
                        UPDATE dim_region
                        SET valid_to = NULL,
                            is_current = 1,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE region_key = :region_key
                        """,
                        {"region_key": same_version_key},
                    )
                    continue
                connection.execute(
                    """
                    UPDATE dim_region
                    SET is_current = 0,
                        valid_to = :valid_to,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE region_code = :region_code
                      AND is_current = 1
                    """,
                    {"valid_to": row["valid_from"], "region_code": row["region_code"]},
                )
                upserts.append(row)
        if not upserts:
            return
        sql = """
            INSERT INTO dim_region (
                region_code, region_name, macro_region, climate_zone, territory_type,
                valid_from, valid_to, is_current, attr_hash_md5, updated_at
            ) VALUES (
                :region_code, :region_name, :macro_region, :climate_zone, :territory_type,
                :valid_from, :valid_to, :is_current, :attr_hash_md5, CURRENT_TIMESTAMP
            )
        """
        connection.executemany(sql, upserts)

    def _load_dim_energy(self, connection: sqlite3.Connection, df: pd.DataFrame) -> None:
        sql = """
            INSERT INTO dim_energy (energy_code, energy_label, unit, is_active, updated_at)
            VALUES (:energy_code, :energy_label, :unit, :is_active, CURRENT_TIMESTAMP)
            ON CONFLICT(energy_code) DO UPDATE SET
                energy_label = excluded.energy_label,
                unit = excluded.unit,
                is_active = excluded.is_active,
                updated_at = CURRENT_TIMESTAMP
        """
        connection.executemany(sql, df.to_dict(orient="records"))

    def _load_dim_weather(self, connection: sqlite3.Connection, df: pd.DataFrame) -> None:
        sql = """
            INSERT INTO dim_weather_context (
                weather_profile_nk, temperature_band, precipitation_band, wind_band,
                humidity_band, weather_profile_label, is_extreme_weather, updated_at
            ) VALUES (
                :weather_profile_nk, :temperature_band, :precipitation_band, :wind_band,
                :humidity_band, :weather_profile_label, :is_extreme_weather, CURRENT_TIMESTAMP
            )
            ON CONFLICT(weather_profile_nk) DO UPDATE SET
                temperature_band = excluded.temperature_band,
                precipitation_band = excluded.precipitation_band,
                wind_band = excluded.wind_band,
                humidity_band = excluded.humidity_band,
                weather_profile_label = excluded.weather_profile_label,
                is_extreme_weather = excluded.is_extreme_weather,
                updated_at = CURRENT_TIMESTAMP
        """
        connection.executemany(sql, df.to_dict(orient="records"))

    def _load_fact(self, connection: sqlite3.Connection, df: pd.DataFrame) -> None:
        sql = """
            INSERT INTO fact_energy_consumption_daily (
                date_key, region_key, energy_key, weather_key, source_name,
                consumption_value, dju_heating, dju_cooling, observation_count, updated_at
            ) VALUES (
                :date_key, :region_key, :energy_key, :weather_key, :source_name,
                :consumption_value, :dju_heating, :dju_cooling, :observation_count, CURRENT_TIMESTAMP
            )
            ON CONFLICT(date_key, region_key, energy_key) DO UPDATE SET
                weather_key = excluded.weather_key,
                source_name = excluded.source_name,
                consumption_value = excluded.consumption_value,
                dju_heating = excluded.dju_heating,
                dju_cooling = excluded.dju_cooling,
                observation_count = excluded.observation_count,
                updated_at = CURRENT_TIMESTAMP
        """
        records = df.where(pd.notna(df), None).to_dict(orient="records")
        connection.executemany(sql, records)

    def _merge_service_table(self, connection: sqlite3.Connection, df: pd.DataFrame) -> None:
        stage_table = "tmp_gold_daily_features_stage"
        connection.execute(f"DROP TABLE IF EXISTS {stage_table}")
        connection.execute(
            f"""
            CREATE TEMP TABLE {stage_table} AS
            SELECT
                feature_date, region, electricity_consumption, gas_consumption,
                temperature_mean, temperature_min, temperature_max, humidity,
                wind_speed, precipitation, dju_heating, dju_cooling, is_weekend,
                month, year, electricity_lag_1, electricity_lag_7, gas_lag_1,
                gas_lag_7, electricity_avg_7d, electricity_avg_30d, gas_avg_7d,
                gas_avg_30d, temperature_avg_7d, dju_heating_sum_7d,
                dju_heating_sum_30d, precipitation_sum_7d, precipitation_sum_30d
            FROM gold_daily_features
            WHERE 1 = 0
            """
        )

        stage_insert_sql = f"""
            INSERT INTO {stage_table} (
                feature_date, region, electricity_consumption, gas_consumption,
                temperature_mean, temperature_min, temperature_max, humidity,
                wind_speed, precipitation, dju_heating, dju_cooling, is_weekend,
                month, year, electricity_lag_1, electricity_lag_7, gas_lag_1,
                gas_lag_7, electricity_avg_7d, electricity_avg_30d, gas_avg_7d,
                gas_avg_30d, temperature_avg_7d, dju_heating_sum_7d,
                dju_heating_sum_30d, precipitation_sum_7d, precipitation_sum_30d
            ) VALUES (
                :feature_date, :region, :electricity_consumption, :gas_consumption,
                :temperature_mean, :temperature_min, :temperature_max, :humidity,
                :wind_speed, :precipitation, :dju_heating, :dju_cooling, :is_weekend,
                :month, :year, :electricity_lag_1, :electricity_lag_7, :gas_lag_1,
                :gas_lag_7, :electricity_avg_7d, :electricity_avg_30d, :gas_avg_7d,
                :gas_avg_30d, :temperature_avg_7d, :dju_heating_sum_7d,
                :dju_heating_sum_30d, :precipitation_sum_7d, :precipitation_sum_30d
            )
        """
        records = df.where(pd.notna(df), None).to_dict(orient="records")
        connection.executemany(stage_insert_sql, records)

        connection.execute(
            f"""
            DELETE FROM gold_daily_features
            WHERE NOT EXISTS (
                SELECT 1
                FROM {stage_table} AS stage
                WHERE stage.feature_date = gold_daily_features.feature_date
                  AND stage.region = gold_daily_features.region
            )
            """
        )

        merge_sql = """
            INSERT INTO gold_daily_features (
                feature_date, region, electricity_consumption, gas_consumption,
                temperature_mean, temperature_min, temperature_max, humidity,
                wind_speed, precipitation, dju_heating, dju_cooling, is_weekend,
                month, year, electricity_lag_1, electricity_lag_7, gas_lag_1,
                gas_lag_7, electricity_avg_7d, electricity_avg_30d, gas_avg_7d,
                gas_avg_30d, temperature_avg_7d, dju_heating_sum_7d,
                dju_heating_sum_30d, precipitation_sum_7d, precipitation_sum_30d,
                updated_at
            ) VALUES (
                :feature_date, :region, :electricity_consumption, :gas_consumption,
                :temperature_mean, :temperature_min, :temperature_max, :humidity,
                :wind_speed, :precipitation, :dju_heating, :dju_cooling, :is_weekend,
                :month, :year, :electricity_lag_1, :electricity_lag_7, :gas_lag_1,
                :gas_lag_7, :electricity_avg_7d, :electricity_avg_30d, :gas_avg_7d,
                :gas_avg_30d, :temperature_avg_7d, :dju_heating_sum_7d,
                :dju_heating_sum_30d, :precipitation_sum_7d, :precipitation_sum_30d,
                CURRENT_TIMESTAMP
            )
            ON CONFLICT(feature_date, region) DO UPDATE SET
                electricity_consumption = excluded.electricity_consumption,
                gas_consumption = excluded.gas_consumption,
                temperature_mean = excluded.temperature_mean,
                temperature_min = excluded.temperature_min,
                temperature_max = excluded.temperature_max,
                humidity = excluded.humidity,
                wind_speed = excluded.wind_speed,
                precipitation = excluded.precipitation,
                dju_heating = excluded.dju_heating,
                dju_cooling = excluded.dju_cooling,
                is_weekend = excluded.is_weekend,
                month = excluded.month,
                year = excluded.year,
                electricity_lag_1 = excluded.electricity_lag_1,
                electricity_lag_7 = excluded.electricity_lag_7,
                gas_lag_1 = excluded.gas_lag_1,
                gas_lag_7 = excluded.gas_lag_7,
                electricity_avg_7d = excluded.electricity_avg_7d,
                electricity_avg_30d = excluded.electricity_avg_30d,
                gas_avg_7d = excluded.gas_avg_7d,
                gas_avg_30d = excluded.gas_avg_30d,
                temperature_avg_7d = excluded.temperature_avg_7d,
                dju_heating_sum_7d = excluded.dju_heating_sum_7d,
                dju_heating_sum_30d = excluded.dju_heating_sum_30d,
                precipitation_sum_7d = excluded.precipitation_sum_7d,
                precipitation_sum_30d = excluded.precipitation_sum_30d,
                updated_at = CURRENT_TIMESTAMP
        """
        connection.executemany(merge_sql, records)
        connection.execute(f"DROP TABLE IF EXISTS {stage_table}")

    @staticmethod
    def _slugify(value: str) -> str:
        normalized = str(value or "").lower()
        normalized = normalized.replace("œ", "oe").replace("æ", "ae").replace("’", "'")
        normalized = (
            unicodedata.normalize("NFKD", normalized)
            .encode("ascii", "ignore")
            .decode("ascii")
            .replace("'", "-")
            .replace("/", "-")
            .replace(" ", "-")
        )
        while "--" in normalized:
            normalized = normalized.replace("--", "-")
        return normalized.strip("-")

    @staticmethod
    def _select_region_name(values: pd.Series) -> str:
        candidates = [str(value).strip() for value in values if str(value).strip()]
        if not candidates:
            return "Unknown"
        return max(
            candidates,
            key=lambda value: (
                any(character.isupper() for character in value),
                any(ord(character) > 127 for character in value),
                "-" in value or " " in value,
                len(value),
            ),
        )

    @staticmethod
    def _merge_source_names(values: pd.Series) -> str:
        unique_sources = sorted({str(value).strip() for value in values if str(value).strip()})
        if not unique_sources:
            return "unknown"
        return ",".join(unique_sources)

    @staticmethod
    def _md5(*values: str) -> str:
        payload = "|".join(value if value is not None else "" for value in values)
        return hashlib.md5(payload.encode("utf-8")).hexdigest()

    @staticmethod
    def _month_to_season(month: int) -> str:
        if month in {12, 1, 2}:
            return "Winter"
        if month in {3, 4, 5}:
            return "Spring"
        if month in {6, 7, 8}:
            return "Summer"
        return "Autumn"

    @staticmethod
    def _temperature_band(value: float | None) -> str:
        if pd.isna(value):
            return "Unknown"
        if value < 0:
            return "Freezing"
        if value < 10:
            return "Cold"
        if value < 20:
            return "Mild"
        if value < 30:
            return "Warm"
        return "Hot"

    @staticmethod
    def _precipitation_band(value: float | None) -> str:
        if pd.isna(value):
            return "Unknown"
        if value == 0:
            return "Dry"
        if value < 2:
            return "Light rain"
        if value < 10:
            return "Rain"
        return "Heavy rain"

    @staticmethod
    def _wind_band(value: float | None) -> str:
        if pd.isna(value):
            return "Unknown"
        if value < 15:
            return "Low wind"
        if value < 35:
            return "Moderate wind"
        if value < 70:
            return "Strong wind"
        return "Storm"

    @staticmethod
    def _humidity_band(value: float | None) -> str:
        if pd.isna(value):
            return "Unknown"
        if value < 40:
            return "Dry air"
        if value < 70:
            return "Balanced humidity"
        return "Humid air"
