-- ============================================================
-- GOLD LAYER (Bloc 3) - Delta Lake target DDL
-- Reference DDL for E5 oral / report / future migration
-- ============================================================

CREATE TABLE IF NOT EXISTS gold.dim_date (
    date_key INT,
    full_date DATE,
    day INT,
    month INT,
    month_name STRING,
    quarter INT,
    year INT,
    week_of_year INT,
    day_of_week INT,
    weekday_label STRING,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    is_school_holiday BOOLEAN,
    season STRING,
    inserted_at TIMESTAMP,
    updated_at TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold.dim_region (
    region_key BIGINT GENERATED ALWAYS AS IDENTITY,
    region_code STRING,
    region_name STRING,
    macro_region STRING,
    climate_zone STRING,
    territory_type STRING,
    valid_from DATE,
    valid_to DATE,
    is_current BOOLEAN,
    attr_hash_md5 STRING,
    inserted_at TIMESTAMP,
    updated_at TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold.dim_energy (
    energy_key BIGINT GENERATED ALWAYS AS IDENTITY,
    energy_code STRING,
    energy_label STRING,
    unit STRING,
    is_active BOOLEAN,
    inserted_at TIMESTAMP,
    updated_at TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold.dim_weather_context (
    weather_key BIGINT GENERATED ALWAYS AS IDENTITY,
    weather_profile_nk STRING,
    temperature_band STRING,
    precipitation_band STRING,
    wind_band STRING,
    humidity_band STRING,
    weather_profile_label STRING,
    is_extreme_weather BOOLEAN,
    inserted_at TIMESTAMP,
    updated_at TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS gold.fact_energy_consumption_daily (
    date_key INT,
    region_key BIGINT,
    energy_key BIGINT,
    weather_key BIGINT,
    source_name STRING,
    consumption_value DOUBLE,
    dju_heating DOUBLE,
    dju_cooling DOUBLE,
    observation_count INT,
    inserted_at TIMESTAMP,
    updated_at TIMESTAMP
) USING DELTA
PARTITIONED BY (date_key);

-- Example optimization for the fact table
-- OPTIMIZE gold.fact_energy_consumption_daily ZORDER BY (region_key, energy_key);
