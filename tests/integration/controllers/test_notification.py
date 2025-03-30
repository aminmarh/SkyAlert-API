import os
import pytest

from unittest.mock import patch, MagicMock
from app import create_app
from flask_jwt_extended import create_access_token
from flask import g
from marshmallow.exceptions import ValidationError


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
def mock_notification_query():
    with patch("app.models.database_model.Notification.query") as mock:
        yield mock


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
def mock_user_query():
    with patch("app.models.database_model.User.query") as mock:
        yield mock


@pytest.fixture
def mock_mark_as_read_schema():
    with patch("app.controllers.notification_controller.MarkAsReadSchema") as mock:
        yield mock


@pytest.fixture
def mock_db_session():
    with patch("app.extensions.db.session") as mock:
        yield mock


@pytest.fixture
def mock_delete_notification_schema():
    with patch("app.schemas.notification_schema.DeleteNotificationSchema") as mock:
        yield mock


def test_get_notifications_success(
    mock_notification_query, mock_jwt_required, mock_get_jwt_identity, client
):
    notification_1 = MagicMock()
    notification_1.id = 1
    notification_1.title = "Flood threshold met for Paris"
    notification_1.message = "User's precipitation threshold: 10 mm - Actual: 10 mm"
    notification_1.is_read = False
    notification_1.created_at = MagicMock()
    notification_1.created_at.isoformat.return_value = "2024-01-01T12:00:00"

    notification_2 = MagicMock()
    notification_2.id = 2
    notification_2.title = "Temperature drop warning"
    notification_2.message = "User's temperature threshold: -5°C - Actual: -10°C"
    notification_2.is_read = True
    notification_2.created_at = MagicMock()
    notification_2.created_at.isoformat.return_value = "2024-01-01T11:00:00"

    mock_notification_query.filter_by.return_value.order_by.return_value.all.return_value = [
        notification_1,
        notification_2,
    ]

    access_token = create_access_token(identity=1)
    response = client.get(
        "/api/notifications",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": [
            {
                "id": 1,
                "title": "Flood threshold met for Paris",
                "message": "User's precipitation threshold: 10 mm - Actual: 10 mm",
                "is_read": False,
                "created_at": "2024-01-01T12:00:00",
            },
            {
                "id": 2,
                "title": "Temperature drop warning",
                "message": "User's temperature threshold: -5°C - Actual: -10°C",
                "is_read": True,
                "created_at": "2024-01-01T11:00:00",
            },
        ],
        "message": "Notifications retrieved successfully",
    }
    mock_notification_query.filter_by.assert_called_once_with(user_id=1)
    mock_notification_query.filter_by.return_value.order_by.assert_called_once()


def test_get_notifications_empty(
    mock_notification_query, mock_jwt_required, mock_get_jwt_identity, client
):
    mock_notification_query.filter_by.return_value.order_by.return_value.all.return_value = (
        []
    )

    access_token = create_access_token(identity=1)
    response = client.get(
        "/api/notifications",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": [],
        "message": "Notifications retrieved successfully",
    }
    mock_notification_query.filter_by.assert_called_once_with(user_id=1)


def test_mark_notification_as_read_success(
    mock_user_query,
    mock_notification_query,
    mock_mark_as_read_schema,
    mock_db_session,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    mock_mark_as_read_schema.return_value.load.return_value = {"notification_id": 1}

    mock_notification = MagicMock()
    mock_notification.id = 1
    mock_notification.is_read = False
    mock_notification_query.filter_by.return_value.first.return_value = (
        mock_notification
    )

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/notifications/mark-read",
        json={"notification_id": 1},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {"notification_id": 1, "is_read": True},
        "message": "Notification marked as read successfully",
    }
    assert mock_notification.is_read is True
    mock_db_session.commit.assert_called_once()


def test_mark_notification_as_read_validation_error(
    mock_mark_as_read_schema,
    mock_user_query,
    mock_notification_query,
    mock_db_session,
    client,
    mock_jwt_required,
    mock_get_jwt_identity,
):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    mock_mark_as_read_schema.return_value.load.side_effect = ValidationError(
        {"notification_id": ["Not a valid integer."]}
    )

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/notifications/mark-read",
        json={"notification_id": "invalid"},
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
        "errors": {"notification_id": ["Not a valid integer."]},
    }

    mock_mark_as_read_schema.return_value.load.assert_called_once_with(
        {"notification_id": "invalid"}
    )


def test_mark_notification_as_read_user_not_found(
    mock_user_query, mock_jwt_required, mock_get_jwt_identity, client
):
    mock_user_query.get.return_value = None

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/notifications/mark-read",
        json={"notification_id": 1},
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


def test_mark_notification_as_read_not_found(
    mock_user_query,
    mock_notification_query,
    mock_mark_as_read_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    # Mock user
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    mock_mark_as_read_schema.return_value.load.return_value = {"notification_id": 1}
    mock_notification_query.filter_by.return_value.first.return_value = None

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/notifications/mark-read",
        json={"notification_id": 1},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Notification not found",
    }


def test_delete_notification_success(
    mock_user_query,
    mock_notification_query,
    mock_db_session,
    mock_delete_notification_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    mock_notification = MagicMock()
    mock_notification.id = 1
    mock_notification.user_id = 1
    mock_notification_query.filter_by.return_value.first.return_value = (
        mock_notification
    )

    mock_delete_notification_schema.return_value.load.return_value = {
        "notification_id": 1
    }

    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/notifications/delete",
        json={"notification_id": 1},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {"notification_id": 1},
        "message": "Notification deleted successfully",
    }
    mock_db_session.delete.assert_called_once_with(mock_notification)
    mock_db_session.commit.assert_called_once()


def test_delete_notification_validation_error(
    mock_delete_notification_schema,
    mock_user_query,
    mock_notification_query,
    mock_db_session,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    mock_delete_notification_schema.return_value.load.side_effect = ValidationError(
        {"notification_id": ["Not a valid integer."]}
    )

    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/notifications/delete",
        json={"notification_id": "invalid"},
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
        "errors": {"notification_id": ["Not a valid integer."]},
    }


def test_delete_notification_user_not_found(
    mock_user_query, mock_jwt_required, mock_get_jwt_identity, client
):
    mock_user_query.get.return_value = None

    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/notifications/delete",
        json={"notification_id": 1},
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


def test_delete_notification_not_found(
    mock_user_query,
    mock_notification_query,
    mock_delete_notification_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    mock_user = MagicMock()
    mock_user.id = 1
    mock_user_query.get.return_value = mock_user

    mock_notification_query.filter_by.return_value.first.return_value = None

    mock_delete_notification_schema.return_value.load.return_value = {
        "notification_id": 1
    }

    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/notifications/delete",
        json={"notification_id": 1},
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Notification not found",
    }
