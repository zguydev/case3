from src.misc import types


class WeatherModel:
    @staticmethod
    def check_bad_weather(weather: types.Weather) -> bool:
        # очень жарко или холодно
        if not 0 <= weather.temperature_c < 35:
            return True
        
        # сильный ветер
        if weather.wind_speed_km_h > 50:
            return True
        
        # идут неприятные осадки: шторм, град
        bad_weather_keywords = ["гром", "шторм", "град"]
        if any(keyword.lower() in weather.weather_text.lower()
               for keyword in bad_weather_keywords):
            return True
        
        # идут осадки и влажно (дождь, снег, но влажно)
        if weather.is_precipitation and weather.precipitation_metric_mm > 5:
            return True
        
        bad_feel_keywords = ["очень", "сыро"]
        if any(bad_feel_keyword in weather.real_feel_temperature_phrase.lower()
               for bad_feel_keyword in bad_feel_keywords):
            return True

        return False

    @staticmethod
    def generate_weather_report_markdown(weather: types.Weather) -> str:
        report = (
            f"Состояние: {weather.weather_text};<br />"
            f"Температура: {weather.temperature_c:.1f}°C;<br />"
            f"Ощущение: {weather.real_feel_temperature_phrase};<br />"
            f"Влажность: {weather.humidity:.1f}%;<br />"
            f"Скорость ветра: {weather.wind_speed_km_h:.1f} км/ч;<br />"
        )
        if weather.is_precipitation:
            report += f"Осадки: {weather.precipitation_metric_mm:.1f} мм;<br />"
        else:
            report += "Осадки: Нет;<br />"
        return report
