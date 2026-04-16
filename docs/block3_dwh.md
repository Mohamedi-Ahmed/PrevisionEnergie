# Bloc 3 - DWH

This note is the short oral support for E5.

- Gold extends Bloc 2 without breaking the existing API layer.
- The target model is a Kimball star schema:
  `fact_energy_consumption_daily` plus `dim_date`, `dim_region`,
  `dim_energy`, `dim_weather_context`.
- The SQLite implementation is the local demo runtime.
- The Delta Lake DDL in `sql/delta/create_gold_tables_delta.sql` is the
  documented target for a more production-like Gold layer.
- The load is idempotent:
  replaying the Silver to Gold load updates facts and dimensions without
  duplicating business rows.
