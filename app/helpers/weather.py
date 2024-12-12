import requests
from flask import current_app


class WeatherAPI:
    BASE_URL = "http://api.weatherapi.com/v1"

    @staticmethod
    def get_forecast(city, days, aqi, alerts):
        api_key = current_app.config.get("WEATHER_API_KEY")
        url = f"{WeatherAPI.BASE_URL}/forecast.json"
        params = {"key": api_key, "q": city, "days": days, "aqi": aqi, "alerts": alerts}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return {"error": "Unable to fetch forecast data"}
