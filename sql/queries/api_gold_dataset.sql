-- Gold dataset query ready for API consumption.
-- Parameters: :region, :start_date, :end_date

SELECT
    feature_date,
    region,
    electricity_consumption,
    gas_consumption,
    temperature_mean,
    dju_heating,
    dju_cooling,
    is_weekend,
    electricity_avg_7d,
    electricity_avg_30d,
    gas_avg_7d,
    gas_avg_30d,
    temperature_avg_7d,
    dju_heating_sum_7d,
    dju_heating_sum_30d,
    precipitation_sum_7d,
    precipitation_sum_30d
FROM gold_daily_features
WHERE region = :region
  AND feature_date >= :start_date
  AND feature_date <= :end_date
ORDER BY feature_date ASC;
