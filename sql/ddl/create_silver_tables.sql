-- ============================================================
-- SILVER LAYER (logical schema)
-- Cleaned / typed / normalized daily dataset
-- SQLite-compatible DDL
-- ============================================================

CREATE TABLE IF NOT EXISTS silver_energy_weather_daily (
    silver_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_name TEXT NOT NULL DEFAULT 'kaggle',
    date TEXT NOT NULL,
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
    year INTEGER,
    month INTEGER,
    weekday INTEGER,
    is_weekend INTEGER,
    record_hash TEXT,
    inserted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_silver_energy_weather_daily UNIQUE (source_name, date, region)
);

-- Main index for C9: equality on region + range filter on date
CREATE INDEX IF NOT EXISTS idx_silver_region_date
    ON silver_energy_weather_daily (region, date);

-- Useful for date-only ranges and future time-based jobs
CREATE INDEX IF NOT EXISTS idx_silver_date
    ON silver_energy_weather_daily (date);

-- Optional support for analytics filtered by year/month
CREATE INDEX IF NOT EXISTS idx_silver_region_year_month
    ON silver_energy_weather_daily (region, year, month);
