from dataclasses import dataclass, field


@dataclass(slots=True)
class SourceSchemaProfile:
    name: str
    column_aliases: dict[str, list[str]] = field(default_factory=dict)
    date_column: str = "date"
    required_columns: list[str] = field(default_factory=lambda: ["date", "region"])
    key_columns: list[str] = field(default_factory=lambda: ["date", "region"])
    numeric_columns: list[str] = field(
        default_factory=lambda: [
            "electricity_consumption",
            "gas_consumption",
            "temperature_mean",
            "temperature_min",
            "temperature_max",
            "humidity",
            "wind_speed",
            "precipitation",
        ]
    )
    categorical_columns: list[str] = field(default_factory=lambda: ["region"])
    dju_heating_base: float = 18.0
    dju_cooling_base: float = 24.0


DEFAULT_COLUMN_ALIASES = {
    "date": ["date", "day", "jour", "datetime", "timestamp"],
    "region": ["region", "area", "zone", "nom_region", "libelle_region", "insee_region"],
    "electricity_consumption": [
        "electricity_consumption",
        "electricity",
        "electricity_mwh",
        "electricity_usage",
        "consumption_electricity",
        "power_consumption",
        "conso_elec_mw",
    ],
    "gas_consumption": [
        "gas_consumption",
        "gas",
        "gas_mwh",
        "gas_usage",
        "consumption_gas",
        "conso_gaz_mw",
    ],
    "temperature_mean": [
        "temperature_mean",
        "temp_mean",
        "avg_temperature",
        "temperature_avg",
        "tavg",
        "tmoy",
    ],
    "temperature_min": ["temperature_min", "temp_min", "min_temperature", "tmin", "temperature_2m_min"],
    "temperature_max": ["temperature_max", "temp_max", "max_temperature", "tmax", "temperature_2m_max"],
    "humidity": ["humidity", "humidite", "relative_humidity"],
    "wind_speed": ["wind_speed", "windspeed", "wind", "vitesse_vent", "wind_speed_10m_max"],
    "precipitation": ["precipitation", "rainfall", "rain", "precipitations", "precipitation_sum", "rain_sum"],
}


def get_schema_profile(source_name: str) -> SourceSchemaProfile:
    return SourceSchemaProfile(name=source_name, column_aliases=DEFAULT_COLUMN_ALIASES)
