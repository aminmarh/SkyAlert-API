import requests
from flask import current_app


class WeatherAPI:
    BASE_URL = "http://api.weatherapi.com/v1"

    @staticmethod
    def get_forecast(city, days, aqi, alerts, preferences):
        api_key = current_app.config.get("WEATHER_API_KEY")
        url = f"{WeatherAPI.BASE_URL}/forecast.json"
        params = {"key": api_key, "q": city, "days": days, "aqi": aqi, "alerts": alerts}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            if preferences.lower() == "imperial":
                data = WeatherAPI.filter_units(data, system="imperial")
            else:
                data = WeatherAPI.filter_units(data, system="metric")
            return data
        return {"error": "Unable to fetch forecast data"}

    @staticmethod
    def filter_units(data, system="metric"):
        """
        Filter the weather data based on the unit system.
        """
        metric_fields = [
            "temp_c",
            "wind_kph",
            "gust_kph",
            "pressure_mb",
            "precip_mm",
            "vis_km",
            "snow_cm",
            "dewpoint_c",
            "feelslike_c",
            "heatindex_c",
            "windchill_c",
        ]
        imperial_fields = [
            "temp_f",
            "wind_mph",
            "gust_mph",
            "pressure_in",
            "precip_in",
            "vis_miles",
            "snow_in",
            "dewpoint_f",
            "feelslike_f",
            "heatindex_f",
            "windchill_f",
        ]

        keep_fields = metric_fields if system == "metric" else imperial_fields

        def filter_obj(obj):
            for field in list(obj.keys()):
                if field not in keep_fields and not isinstance(obj[field], dict):
                    obj.pop(field, None)

        current = data.get("current", {})
        filter_obj(current)

        forecast_days = data.get("forecast", {}).get("forecastday", [])
        for day in forecast_days:
            filter_obj(day.get("day", {}))
            for hour in day.get("hour", []):
                filter_obj(hour)

        return data
