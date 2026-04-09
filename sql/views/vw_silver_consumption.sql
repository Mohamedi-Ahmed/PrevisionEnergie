CREATE VIEW IF NOT EXISTS vw_silver_consumption AS
SELECT
    date,
    region,
    electricity_consumption,
    gas_consumption,
    dju_heating,
    dju_cooling,
    is_weekend,
    month,
    year
FROM silver_energy_weather_daily;
