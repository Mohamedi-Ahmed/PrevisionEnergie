SELECT
    region_key,
    region_code,
    region_name,
    macro_region,
    climate_zone,
    territory_type,
    valid_from,
    valid_to,
    is_current,
    attr_hash_md5
FROM dim_region
ORDER BY region_code, valid_from;
