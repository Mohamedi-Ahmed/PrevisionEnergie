from datetime import date
from typing import Optional

from pydantic import BaseModel


class ConsumptionRecord(BaseModel):
    date: date
    region: str
    electricity_consumption: Optional[float] = None
    gas_consumption: Optional[float] = None
    temperature_mean: Optional[float] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[float] = None
    dju_heating: Optional[float] = None
    dju_cooling: Optional[float] = None
    is_weekend: Optional[int] = None
    month: Optional[int] = None
    year: Optional[int] = None
