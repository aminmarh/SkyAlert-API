import requests
from flask import current_app
from app.schemas.weather_schema import WeatherResponseSchema
from marshmallow import ValidationError


class WeatherAPI:
    BASE_URL = "http://api.weatherapi.com/v1"

    @staticmethod
    def get_forecast(city, days, preferences):
        api_key = current_app.config.get("WEATHER_API_KEY")
        url = f"{WeatherAPI.BASE_URL}/forecast.json"
        params = {"key": api_key, "q": city, "days": days}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            raw_data = response.json()
            system = "imperial" if preferences.lower() == "imperial" else "metric"
            try:
                schema = WeatherResponseSchema()
                schema.system = system
                validated_data = schema.load(raw_data)
                return validated_data
            except ValidationError as err:
                return {
                    "error": "Validation error in API response",
                    "details": err.messages,
                }

        error_messages = {
            401: "Invalid API key",
            404: f"City '{city}' not found",
        }
        return {
            "error": error_messages.get(
                response.status_code, "Unable to fetch forecast data."
            )
        }

    @staticmethod
    def location_search(query):
        api_key = current_app.config.get("WEATHER_API_KEY")
        url = f"{WeatherAPI.BASE_URL}/search.json"
        params = {"key": api_key, "q": query}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            return response.json()

        error_messages = {
            401: "Invalid API key",
            404: f"Query '{query}' not found",
        }
        return {
            "error": error_messages.get(
                response.status_code, "Unable to fetch forecast data."
            )
        }
