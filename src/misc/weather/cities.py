from typing import Any, Optional
import pathlib
import sys

import tomli

from src.misc import types


class Cities:
    @staticmethod
    def _load_config() -> dict[str, types.Location]:
        cities_config_file_path = (pathlib.Path(sys.path[0]) / "config.toml").resolve()
        if not cities_config_file_path.exists():
            raise RuntimeError("config.toml config file not exists")
        
        raw_cities_config: dict[str, Any]
        with open(cities_config_file_path, "r", encoding="utf-8") as file:
            raw_cities_config = tomli.loads(file.read())
        
        cities_config: dict[str, types.Location] = {}
        for city, coords in raw_cities_config["city_coordinates"].items():
            cities_config[city] = types.Location(lat=coords["lat"], lon=coords["lon"])

        return cities_config
    
    @staticmethod
    def city_to_location(city: str) -> Optional[types.Location]:
        cities_config = Cities._load_config()
        
        if not city in cities_config:
            return None
        
        return cities_config[city]
