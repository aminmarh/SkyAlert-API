import os
import pytest
from unittest.mock import patch, MagicMock
from marshmallow import ValidationError
from flask import g
from app import create_app
from flask_jwt_extended import create_access_token


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "jwtsecret")
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_jwt_required():
    with patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request"
    ) as mock_verify_jwt:

        def set_g_context(*args, **kwargs):
            g._jwt_extended_jwt = {"sub": 1}

        mock_verify_jwt.side_effect = set_g_context
        yield mock_verify_jwt


@pytest.fixture
def mock_get_jwt_identity():
    with patch("flask_jwt_extended.get_jwt_identity") as mock:
        mock.return_value = 1
        yield mock


@pytest.fixture
def mock_user():
    with patch("app.controllers.weather_controller.User") as mock:
        yield mock


@pytest.fixture
def mock_weather_api():
    with patch("app.controllers.weather_controller.WeatherAPI") as mock:
        yield mock


@pytest.fixture
def mock_weather_request_schema():
    with patch("app.controllers.weather_controller.WeatherRequestSchema") as mock:
        yield mock


@pytest.fixture
def mock_forecast_data():
    return {
        "current": [{"temp": 15, "condition": "Sunny"}],
        "forecast": [{"date": "2023-10-01", "temp": 16, "condition": "Cloudy"}],
        "location": [{"name": "Paris", "country": "France"}],
    }


@pytest.fixture
def mock_search_location_schema():
    with patch("app.controllers.weather_controller.SearchLocationSchema") as mock:
        yield mock


@pytest.fixture
def mock_location_data():
    return {
        "name": "Paris",
        "region": "Ile-de-France",
        "country": "France",
        "lat": "48.85",
        "lon": "2.35",
        "url": "paris-ile-de-france-france",
    }


def test_get_forecast_success(
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_user,
    mock_weather_api,
    mock_weather_request_schema,
    mock_forecast_data,
    client,
):
    mock_user_instance = MagicMock()
    mock_user_instance.preferences = "metric"
    mock_user.query.get.return_value = mock_user_instance

    mock_weather_request_schema.return_value.load.return_value = {
        "city": "Paris",
        "days": 3,
    }

    mock_weather_api.get_forecast.return_value = mock_forecast_data

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/weather/forecast",
        json={"city": "Paris", "days": 3},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": mock_forecast_data,
        "message": "Weather forecast for Paris retrieved successfully",
    }
    mock_weather_api.get_forecast.assert_called_once_with("Paris", 3, "metric")


def test_get_forecast_validation_error(
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_user,
    mock_weather_request_schema,
    client,
):
    mock_user_instance = MagicMock()
    mock_user_instance.preferences = "metric"
    mock_user.query.get.return_value = mock_user_instance

    mock_weather_request_schema.return_value.load.side_effect = ValidationError(
        {"city": ["City name must be a string containing only letters and spaces"]}
    )

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/weather/forecast",
        json={"city": "123Paris", "days": 3},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {
            "city": ["City name must be a string containing only letters and spaces"]
        },
    }


def test_get_forecast_user_not_found(
    mock_jwt_required, mock_get_jwt_identity, mock_user, client
):
    mock_user.query.get.return_value = None

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/weather/forecast",
        json={"city": "Paris", "days": 3},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "User not found",
    }


def test_get_forecast_api_error(
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_user,
    mock_weather_api,
    mock_weather_request_schema,
    client,
):
    mock_user_instance = MagicMock()
    mock_user_instance.preferences = "metric"
    mock_user.query.get.return_value = mock_user_instance

    mock_weather_request_schema.return_value.load.return_value = {
        "city": "Paris",
        "days": 3,
    }

    mock_weather_api.get_forecast.side_effect = Exception("API error")

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/weather/forecast",
        json={"city": "Paris", "days": 3},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 500
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "An error occurred while retrieving the forecast",
        "errors": "API error",
    }


def test_search_location_success(
    mock_jwt_required,
    mock_search_location_schema,
    mock_weather_api,
    mock_location_data,
    client,
):
    mock_search_location_schema.return_value.load.return_value = {
        "query": "Paris",
    }

    mock_weather_api.location_search.return_value = mock_location_data

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/weather/search",
        json={"query": "Paris"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": mock_location_data,
        "message": "Weather location search for Paris retrieved successfully",
    }
    mock_weather_api.location_search.assert_called_once_with("Paris")


def test_search_location_validation_error(
    mock_jwt_required, mock_search_location_schema, client
):
    mock_search_location_schema.return_value.load.side_effect = ValidationError(
        {"query": ["Query must be a non-empty string"]}
    )

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/weather/search",
        json={"query": ""},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {"query": ["Query must be a non-empty string"]},
    }


def test_search_location_api_error(
    mock_jwt_required, mock_search_location_schema, mock_weather_api, client
):
    mock_search_location_schema.return_value.load.return_value = {
        "query": "Paris",
    }

    mock_weather_api.location_search.side_effect = Exception("API error")

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/weather/search",
        json={"query": "Paris"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 500
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "An error occurred while retrieving the location",
        "errors": "API error",
    }
