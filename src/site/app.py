from typing import Any, Optional

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

from src.misc import types
from src.misc.weather.cities import Cities
from src.misc.weather.model import WeatherModel
from src.site.sync_api import get_weather


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


Cities._load_config()


app.layout = html.Div([
    html.H1("Погода в любое время года"),
    html.H6("2nd Edition Ver. 2.31"),
    html.Div([
        dbc.Col([
            html.Label("Начальный город", style={"padding-right": "20px"}),
            dcc.Input(id="start-city", type="text", placeholder="Москва", debounce=True),
        ], width=6),
        dbc.Col([
            html.Label("Промежуточные города", style={"padding-right": "20px"}),
            dcc.Input(id="intermediate-cities", type="text", placeholder="Казань,Омск", debounce=True),
            html.Div("Введи города через разделитель \",\", например: \"Казань,Омск\", либо оставь пустым", style={"font-size": "12px", "color": "grey"}),
        ]),
        dbc.Col([
            html.Label("Конечный город", style={"padding-right": "20px"}),
            dcc.Input(id="end-city", type="text", placeholder="Владивосток", debounce=True)
        ], width=6)
    ], style={"margin-bottom": "20px"}),

    html.Div([
        html.Label("Период (дни)"),
        dcc.Slider(id="period-slider", min=1, max=5, step=1, value=1, marks={i: f"{i} день" for i in range(1, 7+1)})
    ], style={"margin-bottom": "20px"}),

    html.Label("Выбери величину"),
    dcc.RadioItems(
        id="graph-type",
        options=[
            {"label": "Температура", "value": "temperature"},
            {"label": "Скорость ветра (км/ч)", "value": "wind_speed"},
            {"label": "Кол-во осадков (мм)", "value": "precipitation"}
        ],
        value="temperature",
        inline=True,
    ),

    html.Div(id="error-message", style={"color": "red", "margin-top": "10px"}),

    html.Button("Обновить график", id="update-btn", n_clicks=0),

    dcc.Graph(id="weather-graph"),

    html.Div(id="weather-text", style={"margin-top": "20px"})
])

@app.callback(
    [Output("error-message", "children"), Output("weather-text", "children"), Output("weather-graph", "figure")],
    [Input("update-btn", "n_clicks")],
    [State("start-city", "value"),
     State("end-city", "value"),
     State("intermediate-cities", "value"),
     State("graph-type", "value"),
     State("period-slider", "value")]
)
def update_weather_data(
    _n_clicks: int, start_city: str, end_city: str,
    raw_intermediate_cities: Optional[str], graph_type: str, days: int,
) -> tuple[str, Optional[html.Div], go.Figure]:
    if not (start_city and end_city):
        return "Пожалуйста, введи начальный и конечный город.", None, go.Figure()
    
    fig = go.Figure()
    
    start_city = start_city.strip()
    end_city = end_city.strip()
    
    raw_intermediate_cities = raw_intermediate_cities.strip() if raw_intermediate_cities else ""
    intermediate_cities = list(map(str.strip, raw_intermediate_cities.split(","))) if raw_intermediate_cities else []
    
    cities_route: dict[str, types.Location] = {}
    for city_name in [start_city] + intermediate_cities + [end_city]:
        city_location = Cities.city_to_location(city=city_name)
        if not city_location:
            return f"Город \"{city_name}\" отсутствует в словаре config.toml", None, go.Figure()
        if city_name in cities_route:
            return f"Город \"{city_name}\" повторяется", None, go.Figure()
        
        cities_route[city_name] = city_location

    cities_weather: dict[str, list[types.Weather]] = {}
    for city_name, city_location in cities_route.items():
        try:
            city_weather = get_weather(location=city_location, days=days)
        except Exception as e:
            return f"Error: {e}", None, go.Figure()
        cities_weather[city_name] = city_weather
    
    weather_elements: list[html.Div] = []
    cities_weather_data: dict[str, dict[str, list[float]]] = {}
    for i, city_name in enumerate(cities_route.keys()):
        weather_elements+= [
            html.Div([
                html.P(f"{i+1}. {city_name}"),
                html.Ul([
                    html.Li([
                        html.P(f"День {day}: " + ("👎" if WeatherModel.check_bad_weather(weather) else "👍")),
                        dcc.Markdown(WeatherModel.generate_weather_report_markdown(weather), dangerously_allow_html=True),
                    ]) for day, weather in enumerate(cities_weather[city_name], start=1)
                ]),
            ])
        ]
        
        city_weather_history = {
            "temperature": [t.temperature_c for t in cities_weather[city_name]],
            "wind_speed": [t.wind_speed_km_h for t in cities_weather[city_name]],
            "precipitation": [t.precipitation_metric_mm for t in cities_weather[city_name]],
        }
        cities_weather_data[city_name] = city_weather_history
    
    for i, (city_name, city_weather_history) in enumerate(cities_weather_data.items()):
        y_data = city_weather_history.get(graph_type, [])[:days]
        fig.add_trace(go.Scatter(
            x=list(range(1, days + 1)),
            y=y_data,
            mode="lines+markers",
            name=f"{city_name}",
        ))

    fig.update_layout(
        title=f"Данные погоды метрики {graph_type.capitalize()}",
        xaxis_title="Дни",
        yaxis_title=graph_type.capitalize(),
        template="plotly_white",
    )

    return "", html.Div(weather_elements), fig
