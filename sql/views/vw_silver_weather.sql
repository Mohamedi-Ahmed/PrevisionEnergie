CREATE VIEW IF NOT EXISTS vw_silver_weather AS
SELECT
    date,
    region,
    temperature_mean,
    temperature_min,
    temperature_max,
    humidity,
    wind_speed,
    precipitation,
    dju_heating,
    dju_cooling
FROM silver_energy_weather_daily;
