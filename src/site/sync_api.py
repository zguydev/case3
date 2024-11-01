import asyncio

from src.misc.weather import api
from src.misc import types

from loguru import logger


async def _get_weather(location: types.Location, days: int = 1) -> list[types.Weather]:
    weather_api_client = api.WeatherApiClient(logger=logger)

    weather: list[types.Weather]
    try:
        if days == 1:
            weather = [
                await weather_api_client.get_weather_by_location(
                    location=location,
                )
            ]
        else:
            weather = list(
                (
                    await weather_api_client.get_weather_by_location_in_period(
                        location=location,
                        days=days,
                    )
                ).values()
            )
    finally:
        await weather_api_client._client.close()

    return weather

def get_weather(location: types.Location, days: int = 1) -> list[types.Weather]:
    return asyncio.run(_get_weather(location=location, days=days))
