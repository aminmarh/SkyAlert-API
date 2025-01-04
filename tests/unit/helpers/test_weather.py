import pytest

from flask import Flask
from unittest.mock import patch, MagicMock
from marshmallow import ValidationError
from app.helpers.weather_helper import WeatherAPI


@pytest.fixture
def app_context():
    """Fixture pour configurer le contexte Flask pour les tests."""
    app = Flask(__name__)
    app.config["WEATHER_API_KEY"] = "test_api_key"
    with app.app_context():
        yield app


@patch("app.helpers.weather_helper.requests.get")
def test_get_forecast_success(mock_get, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "location": {"name": "Paris", "region": "", "country": "France"},
        "current": {"temp_c": 20.0, "temp_f": 68.0, "is_day": 1},
        "forecast": {"forecastday": []},
    }
    mock_get.return_value = mock_response

    with patch("app.helpers.weather_helper.WeatherResponseSchema") as mock_schema:
        mock_schema_instance = MagicMock()
        mock_schema_instance.system = "metric"
        mock_schema_instance.load.return_value = {
            "location": {"name": "Paris", "region": "", "country": "France"},
            "current": {"temp_c": 20.0, "temp_f": 68.0, "is_day": 1},
            "forecast": {"forecastday": []},
        }
        mock_schema.return_value = mock_schema_instance

        result = WeatherAPI.get_forecast("Paris", 2, "metric")
        assert result["location"]["name"] == "Paris"
        assert result["current"]["temp_c"] == 20.0


@patch("app.helpers.weather_helper.requests.get")
def test_get_forecast_error_validation(mock_get, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"invalid": "data"}
    mock_get.return_value = mock_response

    with patch("app.helpers.weather_helper.WeatherResponseSchema") as mock_schema:
        mock_schema_instance = MagicMock()
        mock_schema_instance.system = "metric"
        mock_schema_instance.load.side_effect = ValidationError("Validation Error")
        mock_schema.return_value = mock_schema_instance

        result = WeatherAPI.get_forecast("Paris", 2, "metric")
        assert result["error"] == "Validation error in API response"
        assert "details" in result


@patch("app.helpers.weather_helper.requests.get")
def test_get_forecast_error_invalid_api_key(mock_get, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    result = WeatherAPI.get_forecast("Paris", 2, "metric")
    assert result["error"] == "Invalid API key"


@patch("app.helpers.weather_helper.requests.get")
def test_get_forecast_error_city_not_found(mock_get, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = WeatherAPI.get_forecast("UnknownCity", 2, "metric")
    assert result["error"] == "City 'UnknownCity' not found"


@patch("app.helpers.weather_helper.requests.get")
def test_get_forecast_error_generic(mock_get, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = WeatherAPI.get_forecast("Paris", 2, "metric")
    assert result["error"] == "Unable to fetch forecast data."


@patch("app.helpers.weather_helper.requests.get")
def test_location_search_success(mock_get, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"name": "Paris", "region": "", "country": "France"}
    ]
    mock_get.return_value = mock_response

    result = WeatherAPI.location_search("Paris")
    assert len(result) == 1
    assert result[0]["name"] == "Paris"


@patch("app.helpers.weather_helper.requests.get")
def test_location_search_error_invalid_api_key(mock_get, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_get.return_value = mock_response

    result = WeatherAPI.location_search("Paris")
    assert result["error"] == "Invalid API key"


@patch("app.helpers.weather_helper.requests.get")
def test_location_search_error_query_not_found(mock_get, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    result = WeatherAPI.location_search("UnknownQuery")
    assert result["error"] == "Query 'UnknownQuery' not found"


@patch("app.helpers.weather_helper.requests.get")
def test_location_search_error_generic(mock_get, app_context):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_get.return_value = mock_response

    result = WeatherAPI.location_search("Paris")
    assert result["error"] == "Unable to fetch forecast data."
