-- ============================================================
-- C9 - Parameterized extraction query
-- Filters by region and date range
-- Named parameters are SQLAlchemy-friendly: :region, :start_date, :end_date
-- ============================================================

SELECT
    date,
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
WHERE region = :region
  AND date >= :start_date
  AND date <= :end_date
ORDER BY date ASC;
