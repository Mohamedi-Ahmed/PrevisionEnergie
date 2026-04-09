from pathlib import Path
from typing import Any

from app.core.config import BASE_DIR
from app.db.connection import get_connection


class WeatherRepository:
    def __init__(self) -> None:
        self.query = (
            "SELECT date, region, temperature_mean, temperature_min, temperature_max, "
            "humidity, wind_speed, precipitation, dju_heating, dju_cooling "
            "FROM vw_silver_weather "
            "WHERE region = :region AND date >= :start_date AND date <= :end_date "
            "ORDER BY date ASC"
        )

    def fetch_weather(self, start_date: str, end_date: str, region: str) -> list[dict[str, Any]]:
        with get_connection() as connection:
            cursor = connection.execute(
                self.query,
                {
                    "start_date": start_date,
                    "end_date": end_date,
                    "region": region,
                },
            )
            rows = cursor.fetchall()
        return [dict(row) for row in rows]
