import pytest

from marshmallow.exceptions import ValidationError
from app.schemas.weather_schema import (
    WeatherRequestSchema,
    SearchLocationSchema,
    CurrentWeatherSchema,
    DayWeatherSchema,
    HourlyWeatherSchema,
    DailyWeatherSchema,
    ForecastSchema,
    LocationSchema,
    WeatherResponseSchema,
)


def test_weather_request_schema_success():
    valid_data = {"city": "Paris", "days": 2}
    schema = WeatherRequestSchema()
    result = schema.load(valid_data)
    assert result["city"] == "Paris"
    assert result["days"] == 2


def test_weather_request_schema_error_invalid_days():
    invalid_data = {"city": "Paris", "days": 5}
    schema = WeatherRequestSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Days must be either 1, 2 or 3" in str(excinfo.value)


def test_weather_request_schema_error_missing_field():
    invalid_data = {"days": 2}  # Missing 'city'
    schema = WeatherRequestSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_search_location_schema_success():
    valid_data = {"query": "London"}
    schema = SearchLocationSchema()
    result = schema.load(valid_data)
    assert result["query"] == "London"


def test_search_location_schema_error_missing_field():
    invalid_data = {}
    schema = SearchLocationSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_location_schema_success():
    valid_data = {
        "name": "London",
        "region": "England",
        "country": "UK",
        "lat": 51.5074,
        "lon": -0.1278,
        "tz_id": "Europe/London",
        "localtime_epoch": 1622485800,
        "localtime": "2021-05-31 12:30",
    }
    schema = LocationSchema()
    result = schema.load(valid_data)
    assert result["name"] == "London"
    assert result["lat"] == 51.5074


def test_location_schema_error_missing_lat():
    invalid_data = {
        "name": "London",
        "region": "England",
        "country": "UK",
        "lon": -0.1278,
        "tz_id": "Europe/London",
        "localtime_epoch": 1622485800,
        "localtime": "2021-05-31 12:30",
    }
    schema = LocationSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_weather_response_schema_success():
    valid_data = {
        "location": {
            "name": "London",
            "region": "England",
            "country": "UK",
            "lat": 51.5074,
            "lon": -0.1278,
            "tz_id": "Europe/London",
            "localtime_epoch": 1622485800,
            "localtime": "2021-05-31 12:30",
        },
        "current": {
            "last_updated": "2021-05-31 12:00",
            "temp_c": 15.0,
            "temp_f": 59.0,
            "is_day": 1,
            "condition": {
                "code": 1000,
                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                "text": "Sunny",
            },
            "wind_kph": 10.0,
            "wind_mph": 6.2,
            "wind_dir": "NW",
            "precip_mm": 0.0,
            "precip_in": 0.0,
            "humidity": 50,
            "feelslike_c": 15.0,
            "feelslike_f": 59.0,
            "vis_km": 10.0,
            "vis_miles": 6.2,
            "gust_kph": 15.0,
            "gust_mph": 9.3,
        },
        "forecast": {
            "forecastday": [
                {
                    "date": "2021-06-01",
                    "day": {
                        "maxtemp_c": 20.0,
                        "maxtemp_f": 68.0,
                        "mintemp_c": 10.0,
                        "mintemp_f": 50.0,
                        "avgtemp_c": 15.0,
                        "avgtemp_f": 59.0,
                        "totalprecip_mm": 0.0,
                        "totalprecip_in": 0.0,
                        "condition": {
                            "code": 1000,
                            "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                            "text": "Sunny",
                        },
                    },
                    "hour": [
                        {
                            "time": "2021-06-01 00:00",
                            "temp_c": 15.0,
                            "temp_f": 59.0,
                            "is_day": 0,
                            "condition": {
                                "code": 1000,
                                "icon": "//cdn.weatherapi.com/weather/64x64/night/113.png",
                                "text": "Clear",
                            },
                            "wind_kph": 5.0,
                            "wind_mph": 3.1,
                            "wind_dir": "N",
                            "precip_mm": 0.0,
                            "precip_in": 0.0,
                            "humidity": 80,
                            "feelslike_c": 15.0,
                            "feelslike_f": 59.0,
                            "vis_km": 10.0,
                            "vis_miles": 6.2,
                            "gust_kph": 7.0,
                            "gust_mph": 4.3,
                        }
                    ],
                }
            ]
        },
    }
    schema = WeatherResponseSchema()
    result = schema.load(valid_data)
    assert result["location"]["name"] == "London"
    assert result["current"]["temp_c"] == 15.0
    assert result["forecast"]["forecastday"][0]["day"]["maxtemp_c"] == 20.0


def test_weather_response_schema_error_missing_field():
    invalid_data = {
        "location": {},
        "current": {},
        "forecast": {},
    }
    schema = WeatherResponseSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_current_weather_schema_success():
    valid_data = {
        "last_updated": "2023-01-01 12:00",
        "temp_c": 25.0,
        "temp_f": 77.0,
        "is_day": 1,
        "condition": {"code": 1000, "icon": "icon.png", "text": "Sunny"},
        "wind_kph": 10.0,
        "wind_mph": 6.2,
        "wind_dir": "N",
        "precip_mm": 0.0,
        "precip_in": 0.0,
        "humidity": 60,
        "feelslike_c": 25.0,
        "feelslike_f": 77.0,
        "vis_km": 10.0,
        "vis_miles": 6.2,
        "gust_kph": 15.0,
        "gust_mph": 9.3,
    }
    schema = CurrentWeatherSchema()
    result = schema.load(valid_data)
    assert result["temp_c"] == 25.0
    assert result["condition"]["text"] == "Sunny"


def test_current_weather_schema_error_missing_field():
    invalid_data = {
        "temp_c": 25.0,
        "temp_f": 77.0,
    }
    schema = CurrentWeatherSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_day_weather_schema_success():
    valid_data = {
        "maxtemp_c": 30.0,
        "maxtemp_f": 86.0,
        "mintemp_c": 20.0,
        "mintemp_f": 68.0,
        "avgtemp_c": 25.0,
        "avgtemp_f": 77.0,
        "totalprecip_mm": 5.0,
        "totalprecip_in": 0.2,
        "condition": {"code": 1003, "icon": "icon.png", "text": "Partly cloudy"},
    }
    schema = DayWeatherSchema()
    result = schema.load(valid_data)
    assert result["maxtemp_c"] == 30.0
    assert result["condition"]["text"] == "Partly cloudy"


def test_day_weather_schema_error_missing_field():
    invalid_data = {
        "maxtemp_c": 30.0,
        "mintemp_c": 20.0,
    }
    schema = DayWeatherSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_hourly_weather_schema_success():
    valid_data = {
        "time": "2023-01-01 13:00",
        "temp_c": 25.0,
        "temp_f": 77.0,
        "is_day": 1,
        "condition": {"code": 1000, "icon": "icon.png", "text": "Sunny"},
        "wind_kph": 10.0,
        "wind_mph": 6.2,
        "wind_dir": "N",
        "precip_mm": 0.0,
        "precip_in": 0.0,
        "humidity": 60,
        "feelslike_c": 25.0,
        "feelslike_f": 77.0,
        "vis_km": 10.0,
        "vis_miles": 6.2,
        "gust_kph": 15.0,
        "gust_mph": 9.3,
    }
    schema = HourlyWeatherSchema()
    result = schema.load(valid_data)
    assert result["temp_c"] == 25.0
    assert result["condition"]["text"] == "Sunny"


def test_hourly_weather_schema_error_missing_field():
    invalid_data = {
        "temp_c": 25.0,
    }
    schema = HourlyWeatherSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_daily_weather_schema_success():
    valid_data = {
        "date": "2023-01-01",
        "day": {
            "maxtemp_c": 30.0,
            "maxtemp_f": 86.0,
            "mintemp_c": 20.0,
            "mintemp_f": 68.0,
            "avgtemp_c": 25.0,
            "avgtemp_f": 77.0,
            "totalprecip_mm": 5.0,
            "totalprecip_in": 0.2,
            "condition": {"code": 1003, "icon": "icon.png", "text": "Partly cloudy"},
        },
        "hour": [
            {
                "time": "2023-01-01 13:00",
                "temp_c": 25.0,
                "temp_f": 77.0,
                "is_day": 1,
                "condition": {"code": 1000, "icon": "icon.png", "text": "Sunny"},
                "wind_kph": 10.0,
                "wind_mph": 6.2,
                "wind_dir": "N",
                "precip_mm": 0.0,
                "precip_in": 0.0,
                "humidity": 60,
                "feelslike_c": 25.0,
                "feelslike_f": 77.0,
                "vis_km": 10.0,
                "vis_miles": 6.2,
                "gust_kph": 15.0,
                "gust_mph": 9.3,
            }
        ],
    }
    schema = DailyWeatherSchema()
    result = schema.load(valid_data)
    assert result["date"] == "2023-01-01"
    assert result["day"]["maxtemp_c"] == 30.0


def test_daily_weather_schema_error_missing_field():
    invalid_data = {
        "date": "2023-01-01",
    }  # Missing 'day' field
    schema = DailyWeatherSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_forecast_schema_success():
    valid_data = {
        "forecastday": [
            {
                "date": "2023-01-01",
                "day": {
                    "maxtemp_c": 30.0,
                    "maxtemp_f": 86.0,
                    "mintemp_c": 20.0,
                    "mintemp_f": 68.0,
                    "avgtemp_c": 25.0,
                    "avgtemp_f": 77.0,
                    "totalprecip_mm": 5.0,
                    "totalprecip_in": 0.2,
                    "condition": {
                        "code": 1003,
                        "icon": "icon.png",
                        "text": "Partly cloudy",
                    },
                },
                "hour": [
                    {
                        "time": "2023-01-01 13:00",
                        "temp_c": 25.0,
                        "temp_f": 77.0,
                        "is_day": 1,
                        "condition": {
                            "code": 1000,
                            "icon": "icon.png",
                            "text": "Sunny",
                        },
                        "wind_kph": 10.0,
                        "wind_mph": 6.2,
                        "wind_dir": "N",
                        "precip_mm": 0.0,
                        "precip_in": 0.0,
                        "humidity": 60,
                        "feelslike_c": 25.0,
                        "feelslike_f": 77.0,
                        "vis_km": 10.0,
                        "vis_miles": 6.2,
                        "gust_kph": 15.0,
                        "gust_mph": 9.3,
                    }
                ],
            }
        ]
    }
    schema = ForecastSchema()
    result = schema.load(valid_data)
    assert len(result["forecastday"]) == 1


def test_forecast_schema_error_missing_field():
    invalid_data = {}
    schema = ForecastSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)
