-- ============================================================
-- GOLD LAYER - Delta MERGE templates
-- Native Delta equivalent of the SQLite idempotent upserts used
-- in the local runnable demo.
-- ============================================================

MERGE INTO gold.dim_date AS target
USING stage.dim_date AS source
ON target.date_key = source.date_key
WHEN MATCHED THEN UPDATE SET
    target.full_date = source.full_date,
    target.day = source.day,
    target.month = source.month,
    target.month_name = source.month_name,
    target.quarter = source.quarter,
    target.year = source.year,
    target.week_of_year = source.week_of_year,
    target.day_of_week = source.day_of_week,
    target.weekday_label = source.weekday_label,
    target.is_weekend = source.is_weekend,
    target.is_holiday = source.is_holiday,
    target.is_school_holiday = source.is_school_holiday,
    target.season = source.season,
    target.updated_at = current_timestamp()
WHEN NOT MATCHED THEN INSERT (
    date_key, full_date, day, month, month_name, quarter, year,
    week_of_year, day_of_week, weekday_label, is_weekend,
    is_holiday, is_school_holiday, season, inserted_at, updated_at
) VALUES (
    source.date_key, source.full_date, source.day, source.month, source.month_name, source.quarter, source.year,
    source.week_of_year, source.day_of_week, source.weekday_label, source.is_weekend,
    source.is_holiday, source.is_school_holiday, source.season, current_timestamp(), current_timestamp()
);

MERGE INTO gold.dim_energy AS target
USING stage.dim_energy AS source
ON target.energy_code = source.energy_code
WHEN MATCHED THEN UPDATE SET
    target.energy_label = source.energy_label,
    target.unit = source.unit,
    target.is_active = source.is_active,
    target.updated_at = current_timestamp()
WHEN NOT MATCHED THEN INSERT (
    energy_code, energy_label, unit, is_active, inserted_at, updated_at
) VALUES (
    source.energy_code, source.energy_label, source.unit, source.is_active, current_timestamp(), current_timestamp()
);

MERGE INTO gold.dim_weather_context AS target
USING stage.dim_weather_context AS source
ON target.weather_profile_nk = source.weather_profile_nk
WHEN MATCHED THEN UPDATE SET
    target.temperature_band = source.temperature_band,
    target.precipitation_band = source.precipitation_band,
    target.wind_band = source.wind_band,
    target.humidity_band = source.humidity_band,
    target.weather_profile_label = source.weather_profile_label,
    target.is_extreme_weather = source.is_extreme_weather,
    target.updated_at = current_timestamp()
WHEN NOT MATCHED THEN INSERT (
    weather_profile_nk, temperature_band, precipitation_band, wind_band,
    humidity_band, weather_profile_label, is_extreme_weather, inserted_at, updated_at
) VALUES (
    source.weather_profile_nk, source.temperature_band, source.precipitation_band, source.wind_band,
    source.humidity_band, source.weather_profile_label, source.is_extreme_weather, current_timestamp(), current_timestamp()
);

MERGE INTO gold.fact_energy_consumption_daily AS target
USING stage.fact_energy_consumption_daily AS source
ON target.date_key = source.date_key
AND target.region_key = source.region_key
AND target.energy_key = source.energy_key
WHEN MATCHED THEN UPDATE SET
    target.weather_key = source.weather_key,
    target.source_name = source.source_name,
    target.consumption_value = source.consumption_value,
    target.dju_heating = source.dju_heating,
    target.dju_cooling = source.dju_cooling,
    target.observation_count = source.observation_count,
    target.updated_at = current_timestamp()
WHEN NOT MATCHED THEN INSERT (
    date_key, region_key, energy_key, weather_key, source_name,
    consumption_value, dju_heating, dju_cooling, observation_count, inserted_at, updated_at
) VALUES (
    source.date_key, source.region_key, source.energy_key, source.weather_key, source.source_name,
    source.consumption_value, source.dju_heating, source.dju_cooling, source.observation_count, current_timestamp(), current_timestamp()
);

MERGE INTO gold.gold_daily_features AS target
USING stage.gold_daily_features AS source
ON target.feature_date = source.feature_date
AND target.region = source.region
WHEN MATCHED THEN UPDATE SET
    target.electricity_consumption = source.electricity_consumption,
    target.gas_consumption = source.gas_consumption,
    target.temperature_mean = source.temperature_mean,
    target.temperature_min = source.temperature_min,
    target.temperature_max = source.temperature_max,
    target.humidity = source.humidity,
    target.wind_speed = source.wind_speed,
    target.precipitation = source.precipitation,
    target.dju_heating = source.dju_heating,
    target.dju_cooling = source.dju_cooling,
    target.is_weekend = source.is_weekend,
    target.month = source.month,
    target.year = source.year,
    target.electricity_lag_1 = source.electricity_lag_1,
    target.electricity_lag_7 = source.electricity_lag_7,
    target.gas_lag_1 = source.gas_lag_1,
    target.gas_lag_7 = source.gas_lag_7,
    target.electricity_avg_7d = source.electricity_avg_7d,
    target.electricity_avg_30d = source.electricity_avg_30d,
    target.gas_avg_7d = source.gas_avg_7d,
    target.gas_avg_30d = source.gas_avg_30d,
    target.temperature_avg_7d = source.temperature_avg_7d,
    target.dju_heating_sum_7d = source.dju_heating_sum_7d,
    target.dju_heating_sum_30d = source.dju_heating_sum_30d,
    target.precipitation_sum_7d = source.precipitation_sum_7d,
    target.precipitation_sum_30d = source.precipitation_sum_30d,
    target.updated_at = current_timestamp()
WHEN NOT MATCHED THEN INSERT (
    feature_date, region, electricity_consumption, gas_consumption,
    temperature_mean, temperature_min, temperature_max, humidity,
    wind_speed, precipitation, dju_heating, dju_cooling, is_weekend,
    month, year, electricity_lag_1, electricity_lag_7, gas_lag_1, gas_lag_7,
    electricity_avg_7d, electricity_avg_30d, gas_avg_7d, gas_avg_30d,
    temperature_avg_7d, dju_heating_sum_7d, dju_heating_sum_30d,
    precipitation_sum_7d, precipitation_sum_30d, inserted_at, updated_at
) VALUES (
    source.feature_date, source.region, source.electricity_consumption, source.gas_consumption,
    source.temperature_mean, source.temperature_min, source.temperature_max, source.humidity,
    source.wind_speed, source.precipitation, source.dju_heating, source.dju_cooling, source.is_weekend,
    source.month, source.year, source.electricity_lag_1, source.electricity_lag_7, source.gas_lag_1, source.gas_lag_7,
    source.electricity_avg_7d, source.electricity_avg_30d, source.gas_avg_7d, source.gas_avg_30d,
    source.temperature_avg_7d, source.dju_heating_sum_7d, source.dju_heating_sum_30d,
    source.precipitation_sum_7d, source.precipitation_sum_30d, current_timestamp(), current_timestamp()
);
