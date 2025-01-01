import requests
from flask import current_app


class WeatherAPI:
    BASE_URL = "http://api.weatherapi.com/v1"

    METRIC_FIELDS = [
        "temp_c",
        "wind_kph",
        "pressure_mb",
        "precip_mm",
        "feelslike_c",
        "vis_km",
        "gust_kph",
        "windchill_c",
        "heatindex_c",
        "dewpoint_c",
        "maxtemp_c",
        "mintemp_c",
        "avgtemp_c",
        "totalprecip_mm",
        "avgvis_km",
        "snow_cm",
    ]

    IMPERIAL_FIELDS = [
        "temp_f",
        "wind_mph",
        "pressure_in",
        "precip_in",
        "feelslike_f",
        "vis_miles",
        "gust_mph",
        "windchill_f",
        "heatindex_f",
        "dewpoint_f",
        "maxtemp_f",
        "mintemp_f",
        "avgtemp_f",
        "totalprecip_in",
        "avgvis_miles",
    ]

    UNIVERSAL_FIELDS = [
        "last_updated",
        "is_day",
        "condition",
        "wind_degree",
        "wind_dir",
        "humidity",
        "cloud",
        "date",
        "avghumidity",
        "time",
    ]

    @staticmethod
    def get_forecast(city, days, preferences):
        api_key = current_app.config.get("WEATHER_API_KEY")
        url = f"{WeatherAPI.BASE_URL}/forecast.json"
        params = {"key": api_key, "q": city, "days": days}
        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()
            system = "imperial" if preferences.lower() == "imperial" else "metric"
            data = WeatherAPI.filter_units(data, system=system)
            return data

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
    def filter_units(data, system="metric"):
        """
        Filters the weather data to include only the relevant unit system,
        rounds numeric values, and preserves universal fields.
        """
        keep_fields = set(
            WeatherAPI.METRIC_FIELDS
            if system == "metric"
            else WeatherAPI.IMPERIAL_FIELDS
        ).union(WeatherAPI.UNIVERSAL_FIELDS)

        def filter_obj(obj):
            for field in list(obj.keys()):
                if field in keep_fields:
                    # Round numeric fields if needed
                    if isinstance(obj[field], (float, int)):
                        obj[field] = round(obj[field], 1)
                else:
                    # Remove fields not in keep_fields
                    obj.pop(field, None)

        # Process the "current" data
        if "current" in data:
            filter_obj(data["current"])

        # Process forecast data
        if "forecast" in data and "forecastday" in data["forecast"]:
            for day in data["forecast"]["forecastday"]:
                if "day" in day:
                    filter_obj(day["day"])
                if "hour" in day and isinstance(day["hour"], list):
                    for hour in day["hour"]:
                        filter_obj(hour)

        return data
