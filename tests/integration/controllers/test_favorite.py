import os
import pytest
from unittest.mock import patch, MagicMock
from marshmallow import ValidationError
from app import create_app
from flask import g
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
def mock_favorite_city():
    with patch("app.controllers.favorite_controller.FavoriteCity") as mock:
        yield mock


@pytest.fixture
def mock_db_session():
    with patch("app.controllers.favorite_controller.db.session") as mock:
        yield mock


@pytest.fixture
def mock_add_favorite_city_schema():
    with patch("app.controllers.favorite_controller.AddFavoriteCitySchema") as mock:
        yield mock


@pytest.fixture
def mock_delete_favorite_city_schema():
    with patch("app.controllers.favorite_controller.DeleteFavoriteCitySchema") as mock:
        yield mock


def test_add_favorite_city_success(
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_favorite_city,
    mock_db_session,
    mock_add_favorite_city_schema,
    client,
):
    mock_add_favorite_city_schema.return_value.load.return_value = {
        "city": "Paris",
    }

    mock_favorite_city.query.filter_by.return_value.first.return_value = None

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/favorites/add",
        json={"city": "Paris"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 201
    assert response.json == {
        "status": "success",
        "data": {"city": "Paris"},
        "message": "City 'Paris' added to favorites",
    }
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()


def test_add_favorite_city_validation_error(
    mock_jwt_required, mock_get_jwt_identity, mock_add_favorite_city_schema, client
):
    mock_add_favorite_city_schema.return_value.load.side_effect = ValidationError(
        {"city": ["City name must be a string containing only letters and spaces"]}
    )

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/favorites/add",
        json={"city": "123Paris"},
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


def test_add_favorite_city_already_in_favorites(
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_favorite_city,
    mock_add_favorite_city_schema,
    client,
):
    mock_add_favorite_city_schema.return_value.load.return_value = {
        "city": "Paris",
    }

    mock_favorite_city.query.filter_by.return_value.first.return_value = MagicMock()

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/favorites/add",
        json={"city": "Paris"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 409
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "City already in favorites",
    }


def test_remove_favorite_city_success(
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_favorite_city,
    mock_db_session,
    mock_delete_favorite_city_schema,
    client,
):
    mock_delete_favorite_city_schema.return_value.load.return_value = {
        "city": "Paris",
    }

    mock_favorite_city_instance = MagicMock()
    mock_favorite_city.query.filter_by.return_value.first.return_value = (
        mock_favorite_city_instance
    )

    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/favorites/delete",
        json={"city": "Paris"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {"city": "Paris"},
        "message": "City removed from favorites",
    }
    mock_db_session.delete.assert_called_once_with(mock_favorite_city_instance)
    mock_db_session.commit.assert_called_once()


def test_remove_favorite_city_validation_error(
    mock_jwt_required, mock_get_jwt_identity, mock_delete_favorite_city_schema, client
):
    mock_delete_favorite_city_schema.return_value.load.side_effect = ValidationError(
        {"city": ["City name must be a string containing only letters and spaces"]}
    )

    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/favorites/delete",
        json={"city": "123Paris"},
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


def test_remove_favorite_city_not_found(
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_favorite_city,
    mock_delete_favorite_city_schema,
    client,
):
    mock_delete_favorite_city_schema.return_value.load.return_value = {
        "city": "Paris",
    }

    mock_favorite_city.query.filter_by.return_value.first.return_value = None

    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/favorites/delete",
        json={"city": "Paris"},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Favorite city not found",
    }


def test_get_favorite_cities_success(
    mock_jwt_required, mock_get_jwt_identity, mock_favorite_city, client
):
    mock_favorite_city_instance_1 = MagicMock()
    mock_favorite_city_instance_1.id = 1
    mock_favorite_city_instance_1.city = "Paris"

    mock_favorite_city_instance_2 = MagicMock()
    mock_favorite_city_instance_2.id = 2
    mock_favorite_city_instance_2.city = "London"

    mock_favorite_city.query.filter_by.return_value.all.return_value = [
        mock_favorite_city_instance_1,
        mock_favorite_city_instance_2,
    ]

    access_token = create_access_token(identity=1)
    response = client.get(
        "/api/favorites",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": [
            {"id": 1, "city": "Paris"},
            {"id": 2, "city": "London"},
        ],
        "message": "List of favorite cities retrieved successfully",
    }
    mock_favorite_city.query.filter_by.assert_called_once_with(user_id=1)


def test_get_favorite_cities_empty(
    mock_jwt_required, mock_get_jwt_identity, mock_favorite_city, client
):
    mock_favorite_city.query.filter_by.return_value.all.return_value = []

    access_token = create_access_token(identity=1)
    response = client.get(
        "/api/favorites",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": [],
        "message": "List of favorite cities retrieved successfully",
    }
    mock_favorite_city.query.filter_by.assert_called_once_with(user_id=1)
