-- ============================================================
-- C10 - Aggregation / feature construction query
-- Builds rolling features from the Silver layer
-- Historical lookback is preserved before final output filtering
-- ============================================================

WITH base AS (
    SELECT
        date AS feature_date,
        region,
        electricity_consumption,
        gas_consumption,
        temperature_mean,
        temperature_min,
        temperature_max,
        humidity,
        wind_speed,
        precipitation,
        dju_heating,
        dju_cooling,
        is_weekend,
        month,
        year
    FROM silver_energy_weather_daily
    WHERE date <= :end_date
      AND (:region IS NULL OR region = :region)
),
features AS (
    SELECT
        feature_date,
        region,
        electricity_consumption,
        gas_consumption,
        temperature_mean,
        temperature_min,
        temperature_max,
        humidity,
        wind_speed,
        precipitation,
        dju_heating,
        dju_cooling,
        is_weekend,
        month,
        year,
        AVG(electricity_consumption) OVER (
            PARTITION BY region
            ORDER BY feature_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS electricity_avg_7d,
        AVG(electricity_consumption) OVER (
            PARTITION BY region
            ORDER BY feature_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS electricity_avg_30d,
        AVG(gas_consumption) OVER (
            PARTITION BY region
            ORDER BY feature_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS gas_avg_7d,
        AVG(gas_consumption) OVER (
            PARTITION BY region
            ORDER BY feature_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS gas_avg_30d,
        AVG(temperature_mean) OVER (
            PARTITION BY region
            ORDER BY feature_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS temperature_avg_7d,
        SUM(dju_heating) OVER (
            PARTITION BY region
            ORDER BY feature_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS dju_heating_sum_7d,
        SUM(dju_heating) OVER (
            PARTITION BY region
            ORDER BY feature_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS dju_heating_sum_30d,
        SUM(precipitation) OVER (
            PARTITION BY region
            ORDER BY feature_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS precipitation_sum_7d,
        SUM(precipitation) OVER (
            PARTITION BY region
            ORDER BY feature_date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS precipitation_sum_30d
    FROM base
)
SELECT
    feature_date,
    region,
    electricity_consumption,
    gas_consumption,
    temperature_mean,
    temperature_min,
    temperature_max,
    humidity,
    wind_speed,
    precipitation,
    dju_heating,
    dju_cooling,
    is_weekend,
    month,
    year,
    electricity_avg_7d,
    electricity_avg_30d,
    gas_avg_7d,
    gas_avg_30d,
    temperature_avg_7d,
    dju_heating_sum_7d,
    dju_heating_sum_30d,
    precipitation_sum_7d,
    precipitation_sum_30d
FROM features
WHERE feature_date >= :start_date
  AND feature_date <= :end_date
ORDER BY region, feature_date;
