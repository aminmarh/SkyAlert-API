import pytest
from unittest.mock import patch, MagicMock
from flask import g
from flask_jwt_extended import create_access_token
from marshmallow.exceptions import ValidationError
from app import create_app
from app.controllers.threshold_controller import (
    get_cities_with_thresholds_and_thresholds_raw,
)


@pytest.fixture(scope="module")
def app():
    app = create_app()
    app.config["TESTING"] = True
    app.config["JWT_SECRET_KEY"] = "jwtsecret"
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def app_context(app):
    with app.app_context():
        yield


@pytest.fixture
def mock_user_get_query(app_context):
    with patch("app.models.database_model.User.query") as mock:
        yield mock


@pytest.fixture
def mock_user_query():
    with patch("app.models.database_model.User.query") as mock:
        yield mock


@pytest.fixture
def mock_favorite_city_query():
    with patch("app.models.database_model.FavoriteCity.query") as mock:
        yield mock


@pytest.fixture
def mock_storm_threshold_query():
    with patch("app.models.database_model.StormThreshold.query") as mock:
        yield mock


@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock:
        yield mock


@pytest.fixture
def mock_storm_schema():
    with patch("app.schemas.threshold_schema.StormSchema") as mock:
        yield mock


@pytest.fixture
def mock_jwt_required():
    with patch("flask_jwt_extended.view_decorators.verify_jwt_in_request") as mock:

        def set_g_context(*args, **kwargs):
            g._jwt_extended_jwt = {"sub": 1}

        mock.side_effect = set_g_context
        yield mock


@pytest.fixture
def mock_get_jwt_identity():
    with patch("flask_jwt_extended.get_jwt_identity") as mock:
        mock.return_value = 1
        yield mock


@pytest.fixture
def mock_convert_units():
    with patch("app.helpers.generic_helper.convert_units") as mock:
        yield mock


@pytest.fixture
def mock_flood_threshold_query():
    with patch("app.models.database_model.FloodThreshold.query") as mock:
        yield mock


@pytest.fixture
def mock_flood_schema():
    with patch("app.schemas.threshold_schema.FloodSchema") as mock:
        yield mock


@pytest.fixture
def mock_heatwave_threshold_query():
    with patch("app.models.database_model.HeatwaveThreshold.query") as mock:
        yield mock


@pytest.fixture
def mock_heatwave_schema():
    with patch("app.schemas.threshold_schema.HeatwaveSchema") as mock:
        yield mock


@pytest.fixture
def mock_delete_threshold_schema():
    with patch("app.schemas.threshold_schema.DeleteThresholdSchema") as mock:
        yield mock


@pytest.fixture
def mock_get_threshold_schema():
    with patch("app.schemas.threshold_schema.GetThresholdSchema") as mock:
        yield mock


def test_create_storm_threshold_success(
    mock_user_query,
    mock_favorite_city_query,
    mock_storm_threshold_query,
    mock_db_session,
    mock_storm_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_convert_units,
    client,
):
    # Mock l'utilisateur
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "metric"
    mock_user_query.get.return_value = mock_user

    # Mock la ville favorite
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock la validation du schéma
    mock_storm_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "wind_speed": 70,
        "gust_speed": 100,
    }

    # Mock la conversion des unités
    def mock_convert_units_side_effect(value, from_unit, to_unit, unit_type):
        if from_unit == "metric" and to_unit == "imperial":
            if unit_type == "wind_speed":
                return int(
                    value * 0.621371
                )  # Convert wind speed from metric to imperial
        return value

    mock_convert_units.side_effect = mock_convert_units_side_effect

    # Mock no existing threshold
    mock_storm_threshold_query.filter.return_value.first.return_value = None

    # Faire la requête
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/storm",
        json={"favorite_city_id": 1, "wind_speed": 70, "gust_speed": 100},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 201
    assert response.json == {
        "status": "success",
        "data": {
            "favorite_city_id": 1,
            "wind_speed_metric": 70,
            "gust_speed_metric": 100,
            "wind_speed_imperial": 43,  # 70 * 0.621371 ≈ 43
            "gust_speed_imperial": 62,  # 100 * 0.621371 ≈ 62
        },
        "message": "Storm threshold created successfully",
    }
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_create_storm_threshold_validation_error(
    mock_storm_schema, mock_user_query, mock_jwt_required, mock_get_jwt_identity, client
):
    # Mock l'utilisateur
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    # Mock l'erreur de validation
    mock_storm_schema.return_value.load.side_effect = ValidationError(
        {"wind_speed": ["Not a valid number"]}
    )

    # Faire la requête
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/storm",
        json={"favorite_city_id": 1, "wind_speed": "invalid", "gust_speed": 100},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {"wind_speed": ["Not a valid integer."]},
    }


def test_create_storm_threshold_favorite_city_not_found(
    mock_user_query,
    mock_favorite_city_query,
    mock_storm_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock l'utilisateur
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    # Mock la ville favorite non trouvée
    mock_favorite_city_query.get.return_value = None

    # Mock la validation du schéma
    mock_storm_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "wind_speed": 70,
        "gust_speed": 100,
    }

    # Faire la requête
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/storm",
        json={"favorite_city_id": 1, "wind_speed": 70, "gust_speed": 100},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Favorite city not found",
    }


def test_create_storm_threshold_already_exists(
    mock_user_query,
    mock_favorite_city_query,
    mock_storm_threshold_query,
    mock_storm_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock l'utilisateur
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "metric"
    mock_user_query.get.return_value = mock_user

    # Mock la ville favorite
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock la validation du schéma
    mock_storm_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "wind_speed": 70,
        "gust_speed": 100,
    }

    # Mock le seuil existant
    mock_storm_threshold_query.filter.return_value.first.return_value = MagicMock()

    # Faire la requête
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/storm",
        json={"favorite_city_id": 1, "wind_speed": 70, "gust_speed": 100},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "A storm threshold with the same values already exists for this city",
    }


def test_create_storm_threshold_success_imperial_units(
    mock_user_query,
    mock_favorite_city_query,
    mock_storm_threshold_query,
    mock_db_session,
    mock_storm_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_convert_units,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "imperial"  # User preferences set to imperial
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the schema validation
    mock_storm_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "wind_speed": 70,  # Input in imperial units
        "gust_speed": 100,  # Input in imperial units
    }

    # Mock the unit conversion
    def mock_convert_units_side_effect(value, from_unit, to_unit, unit_type):
        if from_unit == "imperial" and to_unit == "metric":
            if unit_type == "wind_speed":
                return int(
                    value * 1.60934
                )  # Convert wind speed from imperial to metric
        return value

    mock_convert_units.side_effect = mock_convert_units_side_effect

    # Mock no existing threshold
    mock_storm_threshold_query.filter.return_value.first.return_value = None

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/storm",
        json={"favorite_city_id": 1, "wind_speed": 70, "gust_speed": 100},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 201
    assert response.json == {
        "status": "success",
        "data": {
            "favorite_city_id": 1,
            "wind_speed_metric": 113,  # 70 mph ≈ 113 km/h
            "gust_speed_metric": 161,  # 100 mph ≈ 161 km/h
            "wind_speed_imperial": 70,  # Input value in imperial units
            "gust_speed_imperial": 100,  # Input value in imperial units
        },
        "message": "Storm threshold created successfully",
    }
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_create_flood_threshold_success(
    mock_user_query,
    mock_favorite_city_query,
    mock_flood_threshold_query,
    mock_db_session,
    mock_flood_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_convert_units,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "metric"
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the schema validation
    mock_flood_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "precipitation": 50,
    }

    # Mock the unit conversion
    mock_convert_units.return_value = 2  # 50 mm ≈ 1.9685 inches, rounded to 2

    # Mock no existing threshold
    mock_flood_threshold_query.filter.return_value.first.return_value = None

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/flood",
        json={"favorite_city_id": 1, "precipitation": 50},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 201
    assert response.json == {
        "status": "success",
        "data": {
            "favorite_city_id": 1,
            "precipitation_metric": 50,
            "precipitation_imperial": 2,  # Updated to match the mock
        },
        "message": "Flood threshold created successfully",
    }
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_create_flood_threshold_validation_error(
    mock_flood_schema, mock_user_query, mock_jwt_required, mock_get_jwt_identity, client
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    # Mock the schema validation error
    mock_flood_schema.return_value.load.side_effect = ValidationError(
        {"precipitation": ["Not a valid integer."]}  # Updated error message
    )

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/flood",
        json={"favorite_city_id": 1, "precipitation": "invalid"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {"precipitation": ["Not a valid integer."]},  # Updated error message
    }


def test_create_flood_threshold_favorite_city_not_found(
    mock_user_query,
    mock_favorite_city_query,
    mock_flood_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city not found
    mock_favorite_city_query.get.return_value = None

    # Mock the schema validation
    mock_flood_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "precipitation": 50,
    }

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/flood",
        json={"favorite_city_id": 1, "precipitation": 50},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Favorite city not found",
    }


def test_create_flood_threshold_already_exists(
    mock_user_query,
    mock_favorite_city_query,
    mock_flood_threshold_query,
    mock_flood_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "metric"
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the schema validation
    mock_flood_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "precipitation": 50,
    }

    # Mock an existing threshold
    mock_flood_threshold_query.filter.return_value.first.return_value = MagicMock()

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/flood",
        json={"favorite_city_id": 1, "precipitation": 50},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "A flood threshold with the same values already exists for this city",
    }


def test_create_flood_threshold_success_imperial_units(
    mock_user_query,
    mock_favorite_city_query,
    mock_flood_threshold_query,
    mock_db_session,
    mock_flood_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_convert_units,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "imperial"  # User preferences set to imperial
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the schema validation
    mock_flood_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "precipitation": 2,  # Input in imperial units (inches)
    }

    # Mock the unit conversion
    def mock_convert_units_side_effect(value, from_unit, to_unit, unit_type):
        if from_unit == "imperial" and to_unit == "metric":
            if unit_type == "precipitation":
                return int(
                    value * 25.4
                )  # Convert precipitation from inches to millimeters
        return value

    mock_convert_units.side_effect = mock_convert_units_side_effect

    # Mock no existing threshold
    mock_flood_threshold_query.filter.return_value.first.return_value = None

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/flood",
        json={"favorite_city_id": 1, "precipitation": 2},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 201
    assert response.json == {
        "status": "success",
        "data": {
            "favorite_city_id": 1,
            "precipitation_metric": 51,  # 2 inches ≈ 50.8 mm, rounded to 51
            "precipitation_imperial": 2,  # Input value in imperial units
        },
        "message": "Flood threshold created successfully",
    }
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_create_heatwave_threshold_success_metric_units(
    mock_user_query,
    mock_favorite_city_query,
    mock_heatwave_threshold_query,
    mock_db_session,
    mock_heatwave_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_convert_units,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "metric"  # User preferences set to metric
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the schema validation
    mock_heatwave_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "temperature": 35,
        "humidity": 80,
    }

    # Mock the unit conversion
    mock_convert_units.return_value = 95  # 35°C ≈ 95°F

    # Mock no existing threshold
    mock_heatwave_threshold_query.filter.return_value.first.return_value = None

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/heatwave",
        json={"favorite_city_id": 1, "temperature": 35, "humidity": 80},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 201
    assert response.json == {
        "status": "success",
        "data": {
            "favorite_city_id": 1,
            "temperature_metric": 35,
            "temperature_imperial": 95,
            "humidity": 80,
        },
        "message": "HeatWave threshold created successfully",
    }
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_create_heatwave_threshold_success_imperial_units(
    mock_user_query,
    mock_favorite_city_query,
    mock_heatwave_threshold_query,
    mock_db_session,
    mock_heatwave_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_convert_units,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "imperial"  # User preferences set to imperial
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the schema validation
    mock_heatwave_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "temperature": 95,  # Input in imperial units (°F)
        "humidity": 80,
    }

    # Mock the unit conversion
    mock_convert_units.return_value = 35  # 95°F ≈ 35°C

    # Mock no existing threshold
    mock_heatwave_threshold_query.filter.return_value.first.return_value = None

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/heatwave",
        json={"favorite_city_id": 1, "temperature": 95, "humidity": 80},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 201
    assert response.json == {
        "status": "success",
        "data": {
            "favorite_city_id": 1,
            "temperature_metric": 35,  # Converted to metric units
            "temperature_imperial": 95,  # Input value in imperial units
            "humidity": 80,
        },
        "message": "HeatWave threshold created successfully",
    }
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_create_heatwave_threshold_validation_error(
    mock_heatwave_schema,
    mock_user_query,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    # Mock the schema validation error
    mock_heatwave_schema.return_value.load.side_effect = ValidationError(
        {"temperature": ["Not a valid number"]}
    )

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/heatwave",
        json={"favorite_city_id": 1, "temperature": "invalid", "humidity": 80},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {"temperature": ["Not a valid integer."]},
    }


def test_create_heatwave_threshold_favorite_city_not_found(
    mock_user_query,
    mock_favorite_city_query,
    mock_heatwave_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city not found
    mock_favorite_city_query.get.return_value = None

    # Mock the schema validation
    mock_heatwave_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "temperature": 35,
        "humidity": 80,
    }

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/heatwave",
        json={"favorite_city_id": 1, "temperature": 35, "humidity": 80},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Favorite city not found",
    }


def test_create_heatwave_threshold_already_exists(
    mock_user_query,
    mock_favorite_city_query,
    mock_heatwave_threshold_query,
    mock_heatwave_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "metric"
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the schema validation
    mock_heatwave_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "temperature": 35,
        "humidity": 80,
    }

    # Mock an existing threshold
    mock_heatwave_threshold_query.filter.return_value.first.return_value = MagicMock()

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds/heatwave",
        json={"favorite_city_id": 1, "temperature": 35, "humidity": 80},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "A heatwave threshold with the same values already exists for this city",
    }


def test_delete_threshold_success(
    mock_favorite_city_query,
    mock_storm_threshold_query,
    mock_db_session,
    mock_delete_threshold_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the threshold
    mock_threshold = MagicMock()
    mock_threshold.id = 2
    mock_storm_threshold_query.filter_by.return_value.first.return_value = (
        mock_threshold
    )

    # Mock the schema validation
    mock_delete_threshold_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "threshold_id": 2,
        "threshold_type": "storm",
    }

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/thresholds/delete",
        json={"favorite_city_id": 1, "threshold_id": 2, "threshold_type": "storm"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {
            "favorite_city_id": 1,
            "threshold_id": 2,
            "threshold_type": "storm",
        },
        "message": "Threshold deleted successfully",
    }
    mock_db_session.delete.assert_called_once_with(mock_threshold)
    mock_db_session.commit.assert_called_once()


def test_delete_threshold_validation_error(
    mock_delete_threshold_schema, mock_jwt_required, mock_get_jwt_identity, client
):
    # Mock the schema validation error
    mock_delete_threshold_schema.return_value.load.side_effect = ValidationError(
        {"threshold_type": ["Invalid Threshold Type"]}
    )

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/thresholds/delete",
        json={"favorite_city_id": 1, "threshold_id": 2, "threshold_type": "invalid"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {"threshold_type": ["Invalid Threshold Type"]},
    }


def test_delete_threshold_favorite_city_not_found(
    mock_favorite_city_query,
    mock_delete_threshold_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the favorite city not found
    mock_favorite_city_query.get.return_value = None

    # Mock the schema validation
    mock_delete_threshold_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "threshold_id": 2,
        "threshold_type": "storm",
    }

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/thresholds/delete",
        json={"favorite_city_id": 1, "threshold_id": 2, "threshold_type": "storm"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Favorite city not found",
    }


def test_delete_threshold_not_found(
    mock_favorite_city_query,
    mock_storm_threshold_query,
    mock_delete_threshold_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the threshold not found
    mock_storm_threshold_query.filter_by.return_value.first.return_value = None

    # Mock the schema validation
    mock_delete_threshold_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "threshold_id": 2,
        "threshold_type": "storm",
    }

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/thresholds/delete",
        json={"favorite_city_id": 1, "threshold_id": 2, "threshold_type": "storm"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Threshold not found",
    }


def test_delete_threshold_success_heatwave(
    mock_favorite_city_query,
    mock_heatwave_threshold_query,
    mock_db_session,
    mock_delete_threshold_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the heatwave threshold
    mock_threshold = MagicMock()
    mock_threshold.id = 2
    mock_heatwave_threshold_query.filter_by.return_value.first.return_value = (
        mock_threshold
    )

    # Mock the schema validation
    mock_delete_threshold_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "threshold_id": 2,
        "threshold_type": "heatwave",
    }

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/thresholds/delete",
        json={"favorite_city_id": 1, "threshold_id": 2, "threshold_type": "heatwave"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {
            "favorite_city_id": 1,
            "threshold_id": 2,
            "threshold_type": "heatwave",
        },
        "message": "Threshold deleted successfully",
    }
    mock_db_session.delete.assert_called_once_with(mock_threshold)
    mock_db_session.commit.assert_called_once()


def test_delete_threshold_success_flood(
    mock_favorite_city_query,
    mock_flood_threshold_query,
    mock_db_session,
    mock_delete_threshold_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the flood threshold
    mock_threshold = MagicMock()
    mock_threshold.id = 2
    mock_flood_threshold_query.filter_by.return_value.first.return_value = (
        mock_threshold
    )

    # Mock the schema validation
    mock_delete_threshold_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
        "threshold_id": 2,
        "threshold_type": "flood",
    }

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/thresholds/delete",
        json={"favorite_city_id": 1, "threshold_id": 2, "threshold_type": "flood"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {
            "favorite_city_id": 1,
            "threshold_id": 2,
            "threshold_type": "flood",
        },
        "message": "Threshold deleted successfully",
    }
    mock_db_session.delete.assert_called_once_with(mock_threshold)
    mock_db_session.commit.assert_called_once()


def test_get_thresholds_success(
    mock_user_query,
    mock_favorite_city_query,
    mock_get_threshold_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "metric"  # User preferences set to metric
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city
    mock_favorite_city = MagicMock()
    mock_favorite_city.id = 1
    mock_favorite_city.storm_thresholds = [
        MagicMock(
            id=1,
            wind_speed_metric=70,
            wind_speed_imperial=43,
            gust_speed_metric=100,
            gust_speed_imperial=62,
            created_at=MagicMock(isoformat=lambda: "2024-01-01T12:00:00"),
        )
    ]
    mock_favorite_city.heatwave_thresholds = [
        MagicMock(
            id=2,
            temperature_metric=35,
            temperature_imperial=95,
            humidity=80,
            created_at=MagicMock(isoformat=lambda: "2024-01-01T11:00:00"),
        )
    ]
    mock_favorite_city.flood_thresholds = [
        MagicMock(
            id=3,
            precipitation_metric=50,
            precipitation_imperial=2,
            created_at=MagicMock(isoformat=lambda: "2024-01-01T10:00:00"),
        )
    ]
    mock_favorite_city_query.get.return_value = mock_favorite_city

    # Mock the schema validation
    mock_get_threshold_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
    }

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds",
        json={"favorite_city_id": 1},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {
            "storm": [
                {
                    "id": 1,
                    "wind_speed": 70,
                    "gust_speed": 100,
                    "created_at": "2024-01-01T12:00:00",
                }
            ],
            "heatwave": [
                {
                    "id": 2,
                    "temperature": 35,
                    "humidity": 80,
                    "created_at": "2024-01-01T11:00:00",
                }
            ],
            "flood": [
                {
                    "id": 3,
                    "precipitation": 50,
                    "created_at": "2024-01-01T10:00:00",
                }
            ],
        },
        "message": "Thresholds retrieved successfully",
    }


def test_get_thresholds_validation_error(
    mock_get_threshold_schema,
    mock_user_query,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    # Mock the schema validation error
    mock_get_threshold_schema.return_value.load.side_effect = ValidationError(
        {"favorite_city_id": ["Not a valid number"]}
    )

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds",
        json={"favorite_city_id": "invalid"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {"favorite_city_id": ["Not a valid integer."]},
    }


def test_get_thresholds_favorite_city_not_found(
    mock_user_query,
    mock_favorite_city_query,
    mock_get_threshold_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    # Mock the favorite city not found
    mock_favorite_city_query.get.return_value = None

    # Mock the schema validation
    mock_get_threshold_schema.return_value.load.return_value = {
        "favorite_city_id": 1,
    }

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/thresholds",
        json={"favorite_city_id": 1},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Favorite city not found",
    }


def test_get_cities_with_thresholds_success(
    mock_user_query,
    mock_favorite_city_query,
    mock_db_session,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    # Mock the favorite cities with thresholds
    mock_city_1 = MagicMock()
    mock_city_1.id = 1
    mock_city_1.city = "Paris"

    mock_city_2 = MagicMock()
    mock_city_2.id = 2
    mock_city_2.city = "London"

    # Mock the query object
    mock_query = MagicMock()
    mock_query.all.return_value = [mock_city_1, mock_city_2]

    # Mock the filter method to return the query object
    mock_favorite_city_query.filter.return_value = mock_query

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.get(
        "/api/thresholds/cities",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Debugging: Print the response body
    print("Response JSON:", response.json)

    # Assertions
    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": [],
        "message": "Cities with thresholds retrieved successfully",
    }


def test_get_cities_with_thresholds_user_not_found(
    mock_user_query, mock_jwt_required, mock_get_jwt_identity, client
):
    # Mock the user not found
    mock_user_query.get.return_value = None

    # Make the request
    access_token = create_access_token(identity=1)
    response = client.get(
        "/api/thresholds/cities",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    # Assertions
    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "User not found",
    }


def test_get_cities_with_thresholds_and_thresholds_raw_success(
    mock_user_query, mock_favorite_city_query, mock_db_session, app_context
):
    # Mock the user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "metric"
    mock_user_query.get.return_value = mock_user

    # Mock the favorite cities and their thresholds
    mock_city_1 = MagicMock()
    mock_city_1.id = 1
    mock_city_1.city = "Paris"
    mock_city_1.storm_thresholds = [
        MagicMock(
            wind_speed_metric=70,
            wind_speed_imperial=43,
            gust_speed_metric=100,
            gust_speed_imperial=62,
        )
    ]
    mock_city_1.heatwave_thresholds = [
        MagicMock(temperature_metric=35, temperature_imperial=95, humidity=80)
    ]
    mock_city_1.flood_thresholds = [
        MagicMock(precipitation_metric=50, precipitation_imperial=2)
    ]

    mock_city_2 = MagicMock()
    mock_city_2.id = 2
    mock_city_2.city = "London"
    mock_city_2.storm_thresholds = []
    mock_city_2.heatwave_thresholds = []
    mock_city_2.flood_thresholds = []

    # Mock the query results
    mock_query = MagicMock()
    mock_query.filter.return_value.filter.return_value.all.return_value = [
        mock_city_1,
        mock_city_2,
    ]
    mock_favorite_city_query.filter.return_value = mock_query

    # Call the function
    result = get_cities_with_thresholds_and_thresholds_raw(user_id=1)

    # Debugging output
    print("Query Result:", result)

    # Assertions
    assert result == []


def test_get_cities_with_thresholds_and_thresholds_raw_user_not_found(
    mock_user_get_query, app_context
):
    # Mock the user not found
    mock_user_get_query.get.return_value = None

    # Call the function and expect a ValueError
    with pytest.raises(ValueError, match="User not found"):
        get_cities_with_thresholds_and_thresholds_raw(user_id=1)


def test_thresholds_parsing_logic(
    mock_user_query, mock_favorite_city_query, mock_db_session, app_context
):
    # Mock user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user.preferences = "metric"
    mock_user_query.get.return_value = mock_user

    # Mock thresholds for a city
    mock_city = MagicMock()
    mock_city.id = 1
    mock_city.city = "Paris"
    mock_city.storm_thresholds = [
        MagicMock(wind_speed_metric=70, gust_speed_metric=100)
    ]
    mock_city.heatwave_thresholds = [MagicMock(temperature_metric=35, humidity=80)]
    mock_city.flood_thresholds = [MagicMock(precipitation_metric=50)]

    # Mock query
    with patch("app.controllers.threshold_controller.db.session") as mock_db_session:
        mock_db_session.query.return_value.filter.return_value.filter.return_value.all.return_value = [
            mock_city
        ]

        # Call the function
        result = get_cities_with_thresholds_and_thresholds_raw(user_id=1)

        # Debugging
        print("Parsed Result:", result)

        # Assertions
        assert len(result) == 1
        city_result = result[0]
        assert city_result["city_id"] == 1
        assert city_result["city_name"] == "Paris"
        assert len(city_result["thresholds"]) == 3

        # Check each threshold type
        storm_threshold = next(
            (t for t in city_result["thresholds"] if t["type"] == "storm"), None
        )
        assert storm_threshold is not None
        assert storm_threshold["details"] == {"wind_speed": 70, "gust_speed": 100}

        heatwave_threshold = next(
            (t for t in city_result["thresholds"] if t["type"] == "heatwave"), None
        )
        assert heatwave_threshold is not None
        assert heatwave_threshold["details"] == {"temperature": 35, "humidity": 80}

        flood_threshold = next(
            (t for t in city_result["thresholds"] if t["type"] == "flood"), None
        )
        assert flood_threshold is not None
        assert flood_threshold["details"] == {"precipitation": 50}
