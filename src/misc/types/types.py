from typing import NewType
import dataclasses


__all__ = ["LocationKey", "Location", "Weather"]


LocationKey = NewType("LocationKey", str)


@dataclasses.dataclass
class Location:
    lat: float
    lon: float


@dataclasses.dataclass
class Weather:
    weather_text: str
    temperature_c: float
    """Measured in Celsius"""
    real_feel_temperature_phrase: str
    humidity: float
    wind_speed_km_h: float
    """Measured in km/h"""
    precipitation_metric_mm: float
    """Measured in mm"""
    is_precipitation: bool
    """is_precipitation"""
