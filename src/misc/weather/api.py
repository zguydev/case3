from __future__ import annotations
import os

import accuweather
import accuweather.exceptions
import dotenv
import loguru
import aiohttp

from src.misc import types


class WeatherApiClient:
    def __init__(self, logger: loguru.Logger) -> None:
        self.logger = logger
        
        dotenv.load_dotenv(dotenv.find_dotenv())
        
        self._client = aiohttp.ClientSession()
        
        API_KEY = os.getenv("ACCUWEATHER_API_KEY", None)
        if not API_KEY:
            raise RuntimeError("Environment variable "
                               "\"ACCUWEATHER_API_KEY\" is not set")
        self.API_KEY = API_KEY

    async def get_weather_by_location(
        self, location: types.Location,
    ) -> types.Weather:
        """Получить данные о погоде по местоположению из координат

        Args:
            location: Координаты, для которых требуется узнать состояние погоды

        Raises:
            RuntimeError
            ValueError
            ...

        Returns:
            types.Weather: Состояние погоды в данный момент для входных координат
        """
        
        accu = accuweather.AccuWeather(
            api_key=self.API_KEY,
            session=self._client,
            latitude=location.lat,
            longitude=location.lon,
            language="ru",
        )
        
        try:
            current_conditions = await accu.async_get_current_conditions()
        except accuweather.exceptions.RequestsExceededError:
            raise RuntimeError("Current ACCUWEATHER_API_KEY ended, quota exceeded")
        except accuweather.exceptions.InvalidApiKeyError:
            raise RuntimeError("Invalid ACCUWEATHER_API_KEY")
        except accuweather.exceptions.InvalidCoordinatesError:
            raise ValueError("Invalid coordinates were passed")
        except accuweather.exceptions.ApiError:
            raise RuntimeError("Error with AccuWeather API")
        except Exception as e:
            raise e
        
        weather_text: str = current_conditions["WeatherText"]
        temperature_celsius: float = current_conditions["Temperature"]["Metric"]["Value"]
        real_feal_temperature_phrase: str = current_conditions["RealFeelTemperatureShade"]["Metric"]["Phrase"]
        humidity: float = current_conditions["RelativeHumidity"]
        wind_speed_km_h: float = current_conditions["Wind"]["Speed"]["Metric"]["Value"]
        precipitation_metric_mm: float = current_conditions["PrecipitationSummary"]["Precipitation"]["Metric"]["Value"]
        is_precipitation: bool = current_conditions["HasPrecipitation"]

        weather = types.Weather(
            weather_text=weather_text,
            temperature_c=temperature_celsius,
            real_feel_temperature_phrase=real_feal_temperature_phrase,
            humidity=humidity,
            wind_speed_km_h=wind_speed_km_h,
            precipitation_metric_mm=precipitation_metric_mm,
            is_precipitation=is_precipitation,
        )
        return weather

    async def get_weather_by_location_in_period(
        self, location: types.Location, days: int=7,
    ) -> dict[int, types.Weather]:
        """Получить данные о погоде по местоположению из координат
        на период (по дефолту на 7 дней - неделю)

        Args:
            location: Координаты, для которых требуется узнать состояние погоды
            days: Количество дней (по дефолту на 7 дней - неделю)

        Raises:
            RuntimeError
            ValueError
            ...

        Returns:
            dict[
                int: Индекс дня
                types.Weather: Состояние погоды в день
            ]
        """
        if days <= 0:
            raise ValueError("days must be >= 0")
        
        accu = accuweather.AccuWeather(
            api_key=self.API_KEY,
            session=self._client,
            latitude=location.lat,
            longitude=location.lon,
            language="ru",
        )
        
        weather_for_period: dict[int, types.Weather] = {}
        try:
            daily_forecast = (await accu.async_get_daily_forecast(
                days=5,
            ))[:days]
        except accuweather.exceptions.RequestsExceededError:
            raise RuntimeError("Current ACCUWEATHER_API_KEY ended, quota exceeded")
        except accuweather.exceptions.InvalidApiKeyError:
            raise RuntimeError("Invalid ACCUWEATHER_API_KEY")
        except accuweather.exceptions.InvalidCoordinatesError:
            raise ValueError("Invalid coordinates were passed")
        except accuweather.exceptions.ApiError:
            raise RuntimeError("Error with AccuWeather API")
        except Exception as e:
            raise e
        
        for day, raw_forecast in enumerate(daily_forecast):
            weather_text: str = raw_forecast["ShortPhraseDay"]
            temperature_celsius: float = raw_forecast["TemperatureMax"]["Value"]
            real_feal_temperature_phrase: str = raw_forecast["RealFeelTemperatureMax"]["Phrase"]
            humidity: float = raw_forecast["RelativeHumidityDay"]["Average"]
            wind_speed_km_h: float = raw_forecast["WindDay"]["Speed"]["Value"]
            precipitation_metric_mm: float = raw_forecast["HoursOfPrecipitationDay"]
            is_precipitation: bool = raw_forecast["HasPrecipitationDay"]
            
            forecast = types.Weather(
                weather_text=weather_text,
                temperature_c=temperature_celsius,
                real_feel_temperature_phrase=real_feal_temperature_phrase,
                humidity=humidity,
                wind_speed_km_h=wind_speed_km_h,
                precipitation_metric_mm=precipitation_metric_mm,
                is_precipitation=is_precipitation,
            )
            weather_for_period[day] = forecast

        return weather_for_period
