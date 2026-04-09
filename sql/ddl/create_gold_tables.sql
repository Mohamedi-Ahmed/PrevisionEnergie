-- ============================================================
-- GOLD LAYER (Bloc 3)
-- Star schema + service table for API / analytics
-- SQLite-compatible DDL
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT,
    quarter INTEGER NOT NULL,
    year INTEGER NOT NULL,
    week_of_year INTEGER,
    day_of_week INTEGER NOT NULL,
    weekday_label TEXT,
    is_weekend INTEGER NOT NULL DEFAULT 0,
    is_holiday INTEGER NOT NULL DEFAULT 0,
    is_school_holiday INTEGER NOT NULL DEFAULT 0,
    season TEXT,
    inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dim_date_year_month
    ON dim_date (year, month);

CREATE TABLE IF NOT EXISTS dim_region (
    region_key INTEGER PRIMARY KEY AUTOINCREMENT,
    region_code TEXT NOT NULL,
    region_name TEXT NOT NULL,
    macro_region TEXT,
    climate_zone TEXT,
    territory_type TEXT,
    valid_from TEXT NOT NULL,
    valid_to TEXT,
    is_current INTEGER NOT NULL DEFAULT 1,
    attr_hash_md5 TEXT NOT NULL,
    inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_dim_region_version UNIQUE (region_code, valid_from)
);

CREATE INDEX IF NOT EXISTS idx_dim_region_current
    ON dim_region (region_code, is_current);

CREATE TABLE IF NOT EXISTS dim_energy (
    energy_key INTEGER PRIMARY KEY AUTOINCREMENT,
    energy_code TEXT NOT NULL UNIQUE,
    energy_label TEXT NOT NULL UNIQUE,
    unit TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_weather_context (
    weather_key INTEGER PRIMARY KEY AUTOINCREMENT,
    weather_profile_nk TEXT NOT NULL UNIQUE,
    temperature_band TEXT,
    precipitation_band TEXT,
    wind_band TEXT,
    humidity_band TEXT,
    weather_profile_label TEXT,
    is_extreme_weather INTEGER NOT NULL DEFAULT 0,
    inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fact_energy_consumption_daily (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date_key INTEGER NOT NULL,
    region_key INTEGER NOT NULL,
    energy_key INTEGER NOT NULL,
    weather_key INTEGER,
    source_name TEXT NOT NULL DEFAULT 'kaggle',
    consumption_value REAL,
    dju_heating REAL,
    dju_cooling REAL,
    observation_count INTEGER NOT NULL DEFAULT 1,
    inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_fact_energy_daily UNIQUE (date_key, region_key, energy_key),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (region_key) REFERENCES dim_region(region_key),
    FOREIGN KEY (energy_key) REFERENCES dim_energy(energy_key),
    FOREIGN KEY (weather_key) REFERENCES dim_weather_context(weather_key)
);

CREATE INDEX IF NOT EXISTS idx_fact_region_date
    ON fact_energy_consumption_daily (region_key, date_key);

CREATE INDEX IF NOT EXISTS idx_fact_energy_date
    ON fact_energy_consumption_daily (energy_key, date_key);

CREATE INDEX IF NOT EXISTS idx_fact_weather
    ON fact_energy_consumption_daily (weather_key);

-- ------------------------------------------------------------
-- Service table kept for compatibility with Bloc 2 API / marts
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS gold_daily_features (
    gold_id INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_date TEXT NOT NULL,
    region TEXT NOT NULL,
    electricity_consumption REAL,
    gas_consumption REAL,
    temperature_mean REAL,
    temperature_min REAL,
    temperature_max REAL,
    humidity REAL,
    wind_speed REAL,
    precipitation REAL,
    dju_heating REAL,
    dju_cooling REAL,
    is_weekend INTEGER,
    month INTEGER,
    year INTEGER,
    electricity_avg_7d REAL,
    electricity_avg_30d REAL,
    gas_avg_7d REAL,
    gas_avg_30d REAL,
    temperature_avg_7d REAL,
    dju_heating_sum_7d REAL,
    dju_heating_sum_30d REAL,
    precipitation_sum_7d REAL,
    precipitation_sum_30d REAL,
    inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_gold_daily_features UNIQUE (feature_date, region)
);

CREATE INDEX IF NOT EXISTS idx_gold_region_feature_date
    ON gold_daily_features (region, feature_date);

CREATE INDEX IF NOT EXISTS idx_gold_feature_date
    ON gold_daily_features (feature_date);
