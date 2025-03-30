import os
import pytest

from unittest.mock import patch, MagicMock, call
from marshmallow import ValidationError
from app import create_app
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from flask import g


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


@pytest.fixture(autouse=True)
def mock_sqlalchemy():
    with patch("app.controllers.auth_controller.db") as mock_db:
        mock_db.session = MagicMock()
        yield mock_db


@pytest.fixture
def mock_request_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }


@pytest.fixture
def mock_user_query():
    with patch("app.controllers.auth_controller.User.query") as mock:
        yield mock


@pytest.fixture
def mock_reset_code():
    with patch("app.controllers.auth_controller.ResetCode") as mock:
        yield mock


@pytest.fixture
def mock_db_operations():
    with patch("app.controllers.auth_controller.db.session.add") as mock_add, patch(
        "app.controllers.auth_controller.db.session.commit"
    ) as mock_commit:
        yield mock_add, mock_commit


@pytest.fixture
def mock_send_email():
    with patch("app.controllers.auth_controller.Email.send_email") as mock:
        yield mock


@pytest.fixture
def mock_verif_mail_request_data():
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
        "code": "123456",
    }


@pytest.fixture
def mock_verif_mail_reset_code():
    with patch("app.controllers.auth_controller.ResetCode") as mock:
        yield mock


@pytest.fixture
def mock_verif_mail_user():
    with patch("app.controllers.auth_controller.User") as mock:
        yield mock


@pytest.fixture
def mock_verif_mail_schema():
    with patch("app.controllers.auth_controller.VerifyEmailCodeSchema") as mock:
        yield mock


@pytest.fixture
def mock_login_request_data():
    return {
        "email": "test@example.com",
        "password": "password123",
    }


@pytest.fixture
def mock_login_schema():
    with patch("app.controllers.auth_controller.LoginSchema") as mock:
        yield mock


@pytest.fixture
def mock_create_access_token():
    with patch("app.controllers.auth_controller.create_access_token") as mock:
        yield mock


@pytest.fixture
def mock_update_user_request_data():
    return {
        "username": "new_username",
        "email": "new_email@example.com",
        "preferences": "metric",
    }


@pytest.fixture
def mock_user_update_schema():
    with patch("app.controllers.auth_controller.UserUpdateSchema") as mock:
        yield mock


@pytest.fixture
def mock_user():
    with patch("app.controllers.auth_controller.User") as mock:
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
    with patch("flask_jwt_extended.get_jwt_identity") as mock_identity:
        mock_identity.return_value = 1
        yield mock_identity


@pytest.fixture
def mock_update_password_request_data():
    return {
        "current_password": "current_password_example",
        "new_password": "new_password_example",
    }


@pytest.fixture
def mock_password_update_schema():
    with patch("app.controllers.auth_controller.PasswordUpdateSchema") as mock:
        yield mock


@pytest.fixture
def mock_reset_code_query():
    with patch("app.controllers.auth_controller.ResetCode.query") as mock:
        yield mock


@pytest.fixture
def mock_verify_reset_code_schema():
    with patch("app.controllers.auth_controller.VerifyPasswordResetCodeSchema") as mock:
        yield mock


@pytest.fixture
def mock_password_forgot_schema():
    with patch("app.controllers.auth_controller.PasswordForgotSchema") as mock:
        yield mock


@pytest.fixture
def mock_add_token_to_blacklist():
    with patch("app.controllers.auth_controller.add_token_to_blacklist") as mock:
        yield mock


@pytest.fixture
def mock_delete_jwt_required():
    with patch(
        "flask_jwt_extended.view_decorators.verify_jwt_in_request"
    ) as mock_verify_jwt:

        def set_g_context(*args, **kwargs):
            g._jwt_extended_jwt = {
                "sub": 1,
                "jti": "some_jti",
                "exp": datetime.utcnow().timestamp(),
            }

        mock_verify_jwt.side_effect = set_g_context
        yield mock_verify_jwt


@pytest.fixture
def mock_logout_get_jwt():
    with patch("flask_jwt_extended.get_jwt") as mock_jwt:
        yield mock_jwt


def test_register_success(
    mock_user_query, mock_reset_code, mock_db_operations, mock_request_data, client
):
    mock_add, mock_commit = mock_db_operations
    mock_user_query.filter_by.return_value.first.return_value = None
    mock_reset_code.return_value = MagicMock()

    response = client.post(
        "/api/auth/register",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 201
    assert response.json == {
        "status": "success",
        "data": None,
        "message": "Verification email sent successfully",
    }
    mock_add.assert_called_once()
    mock_commit.assert_called_once()


def test_register_email_already_registered(
    mock_user_query, mock_db_operations, mock_request_data, client
):
    mock_add, mock_commit = mock_db_operations
    mock_user_query.filter_by.return_value.first.return_value = MagicMock()

    response = client.post(
        "/api/auth/register",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 409
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Email already registered",
    }
    mock_add.assert_not_called()
    mock_commit.assert_not_called()


def test_register_email_failure(
    mock_user_query,
    mock_reset_code,
    mock_db_operations,
    mock_send_email,
    mock_request_data,
    client,
):
    mock_add, mock_commit = mock_db_operations
    mock_user_query.filter_by.return_value.first.return_value = None
    mock_send_email.side_effect = Exception("Email service error")
    mock_reset_code.return_value = MagicMock()

    response = client.post(
        "/api/auth/register",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 500
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Failed to send email: Email service error",
    }
    mock_add.assert_called_once_with(mock_reset_code.return_value)
    mock_commit.assert_has_calls([call(), call()])


def test_register_validation_error(client):
    with patch(
        "app.controllers.auth_controller.RegisterSchema"
    ) as mock_register_schema:
        mock_register_schema.return_value.load.side_effect = ValidationError(
            {
                "email": ["Not a valid email address"],
                "password": ["Length must be at least 6."],
            }
        )

        mock_request_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "short",
        }
        response = client.post(
            "/api/auth/register",
            json=mock_request_data,
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        assert response.json == {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": {
                "email": ["Not a valid email address"],
                "password": ["Length must be at least 6."],
            },
        }


def test_verif_mail_success(
    mock_verif_mail_schema,
    mock_verif_mail_reset_code,
    mock_verif_mail_user,
    mock_verif_mail_request_data,
    client,
):
    mock_verif_mail_schema.return_value.load.return_value = mock_verif_mail_request_data

    mock_reset_code_instance = MagicMock()
    mock_reset_code_instance.created_at = datetime.utcnow() - timedelta(minutes=10)
    mock_verif_mail_reset_code.query.filter_by.return_value.first.return_value = (
        mock_reset_code_instance
    )

    mock_user_instance = MagicMock()
    mock_verif_mail_user.return_value = mock_user_instance

    response = client.post(
        "/api/auth/verify-email",
        json=mock_verif_mail_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {"username": "testuser", "email": "test@example.com"},
        "message": "User registered successfully",
    }


def test_verif_mail_validation_error(mock_verif_mail_schema, client):
    mock_verif_mail_schema.return_value.load.side_effect = ValidationError(
        {
            "email": ["Not a valid email address"],
            "code": ["Length must be between 6 and 6."],
        }
    )

    mock_request_data = {
        "username": "testuser",
        "email": "invalid-email",
        "password": "password123",
        "code": "123",
    }

    response = client.post(
        "/api/auth/verify-email",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {
            "email": ["Not a valid email address"],
            "code": ["Length must be between 6 and 6."],
        },
    }


def test_verif_mail_invalid_or_expired_code(
    mock_verif_mail_schema,
    mock_verif_mail_reset_code,
    mock_verif_mail_request_data,
    client,
):
    mock_verif_mail_schema.return_value.load.return_value = mock_verif_mail_request_data

    mock_verif_mail_reset_code.query.filter_by.return_value.first.return_value = None

    response = client.post(
        "/api/auth/verify-email",
        json=mock_verif_mail_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Invalid or expired code",
    }


def test_verif_mail_code_expired(
    mock_verif_mail_schema,
    mock_verif_mail_reset_code,
    mock_verif_mail_request_data,
    client,
):
    mock_verif_mail_schema.return_value.load.return_value = mock_verif_mail_request_data

    mock_reset_code_instance = MagicMock()
    mock_reset_code_instance.created_at = datetime.utcnow() - timedelta(minutes=20)
    mock_verif_mail_reset_code.query.filter_by.return_value.first.return_value = (
        mock_reset_code_instance
    )

    response = client.post(
        "/api/auth/verify-email",
        json=mock_verif_mail_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 410
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Code expired",
    }


def test_login_success(
    mock_login_schema,
    mock_user,
    mock_create_access_token,
    mock_login_request_data,
    client,
):
    mock_login_schema.return_value.load.return_value = mock_login_request_data

    mock_user_instance = MagicMock()
    mock_user_instance.id = 1
    mock_user_instance.username = "testuser"
    mock_user_instance.check_password.return_value = True
    mock_user.query.filter_by.return_value.first.return_value = mock_user_instance

    mock_create_access_token.return_value = "fake_access_token"

    response = client.post(
        "/api/auth/login",
        json=mock_login_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {"access_token": "fake_access_token", "username": "testuser"},
        "message": "Login successful",
    }


def test_login_validation_error(mock_login_schema, client):
    mock_login_schema.return_value.load.side_effect = ValidationError(
        {"email": ["Not a valid email address"]}
    )

    mock_request_data = {
        "email": "invalid-email",
        "password": "password123",
    }

    response = client.post(
        "/api/auth/login",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {"email": ["Not a valid email address"]},
    }


def test_login_invalid_credentials(
    mock_login_schema, mock_user, mock_login_request_data, client
):
    mock_login_schema.return_value.load.return_value = mock_login_request_data

    mock_user.query.filter_by.return_value.first.return_value = None

    response = client.post(
        "/api/auth/login",
        json=mock_login_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 401
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Invalid credentials",
        "code": "INVALID_CREDENTIALS",
    }


def test_update_user_success(
    mock_user_update_schema,
    mock_user,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_update_user_request_data,
    client,
):
    mock_user_update_schema.return_value.load.return_value = (
        mock_update_user_request_data
    )

    mock_user_instance = MagicMock()
    mock_user_instance.id = 1
    mock_user_instance.username = "old_username"
    mock_user_instance.email = "old_email@example.com"
    mock_user_instance.preferences = "imperial"
    mock_user.query.get.return_value = mock_user_instance

    mock_user.query.filter.return_value.first.return_value = None

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/auth/update/user",
        json=mock_update_user_request_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {
            "user": {
                "id": 1,
                "username": "new_username",
                "email": "new_email@example.com",
                "preferences": "metric",
            }
        },
        "message": "User updated successfully",
    }


def test_update_user_validation_error(
    mock_user_update_schema, mock_jwt_required, mock_get_jwt_identity, client
):
    mock_user_update_schema.return_value.load.side_effect = ValidationError(
        {"email": ["Not a valid email address"]}
    )

    mock_request_data = {
        "username": "new_username",
        "email": "invalid-email",
        "preferences": "metric",
    }

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/auth/update/user",
        json=mock_request_data,
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
        "errors": {"email": ["Not a valid email address"]},
    }


def test_update_user_not_found(
    mock_user_update_schema,
    mock_user,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_update_user_request_data,
    client,
):
    mock_user_update_schema.return_value.load.return_value = (
        mock_update_user_request_data
    )

    mock_user.query.get.return_value = None

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/auth/update/user",
        json=mock_update_user_request_data,
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


def test_update_user_email_already_taken(
    mock_user_update_schema,
    mock_user,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_update_user_request_data,
    client,
):
    mock_user_update_schema.return_value.load.return_value = (
        mock_update_user_request_data
    )

    mock_user_instance = MagicMock()
    mock_user_instance.id = 1
    mock_user_instance.email = "old_email@example.com"
    mock_user.query.get.return_value = mock_user_instance

    mock_user.query.filter.return_value.first.return_value = MagicMock()

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/auth/update/user",
        json=mock_update_user_request_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 409
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Email already taken",
    }


def test_update_user_no_changes_detected(
    mock_user_update_schema,
    mock_user,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_update_user_request_data,
    client,
):
    mock_user_update_schema.return_value.load.return_value = (
        mock_update_user_request_data
    )

    mock_user_instance = MagicMock()
    mock_user_instance.id = 1
    mock_user_instance.username = "new_username"
    mock_user_instance.email = "new_email@example.com"
    mock_user_instance.preferences = "metric"
    mock_user.query.get.return_value = mock_user_instance

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/auth/update/user",
        json=mock_update_user_request_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "No changes detected",
    }


def test_update_password_success(
    mock_password_update_schema,
    mock_user,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_update_password_request_data,
    mock_sqlalchemy,
    client,
):
    with patch(
        "app.controllers.auth_controller.check_password_hash"
    ) as mock_check_password_hash:

        mock_password_update_schema.return_value.load.return_value = (
            mock_update_password_request_data
        )

        mock_user_instance = MagicMock()
        mock_user_instance.id = 1
        mock_user_instance.password_hash = "hashed_password"
        mock_user.query.get.return_value = mock_user_instance

        mock_check_password_hash.return_value = True

        mock_get_jwt_identity.return_value = 1

        access_token = create_access_token(identity=1)
        response = client.put(
            "/api/auth/password/update",
            json=mock_update_password_request_data,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
            },
        )

        assert response.status_code == 200
        assert response.json == {
            "status": "success",
            "data": None,
            "message": "Password updated successfully",
        }
        mock_user_instance.set_password.assert_called_once_with("new_password_example")
        mock_sqlalchemy.session.commit.assert_called_once()


def test_update_password_validation_error(
    mock_password_update_schema,
    mock_jwt_required,
    mock_get_jwt_identity,
    client,
):
    mock_password_update_schema.return_value.load.side_effect = ValidationError(
        {"new_password": ["Shorter than minimum length 6"]}
    )

    mock_request_data = {
        "current_password": "current_password_example",
        "new_password": "short",
    }

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/auth/password/update",
        json=mock_request_data,
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
        "errors": {"new_password": ["Shorter than minimum length 6"]},
    }


def test_update_password_incorrect_current_password(
    mock_password_update_schema,
    mock_user,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_update_password_request_data,
    mock_sqlalchemy,
    client,
):
    mock_password_update_schema.return_value.load.return_value = (
        mock_update_password_request_data
    )

    mock_user_instance = MagicMock()
    mock_user_instance.id = 1
    mock_user_instance.password_hash = "hashed_password"
    mock_user_instance.check_password.return_value = False
    mock_user.query.get.return_value = mock_user_instance

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/auth/password/update",
        json=mock_update_password_request_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 403
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Current password is incorrect",
    }
    mock_sqlalchemy.session.commit.assert_not_called()


def test_update_password_user_not_found(
    mock_password_update_schema,
    mock_user,
    mock_jwt_required,
    mock_get_jwt_identity,
    mock_update_password_request_data,
    mock_sqlalchemy,
    client,
):

    mock_password_update_schema.return_value.load.return_value = (
        mock_update_password_request_data
    )
    mock_user.query.get.return_value = None

    access_token = create_access_token(identity=1)
    response = client.put(
        "/api/auth/password/update",
        json=mock_update_password_request_data,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 403
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Current password is incorrect",
    }
    mock_sqlalchemy.session.commit.assert_not_called()


def test_request_password_reset_success(
    mock_user_query, mock_db_operations, mock_send_email, client
):
    mock_add, mock_commit = mock_db_operations
    user_instance = MagicMock()
    user_instance.email = "testuser@example.com"
    mock_user_query.filter_by.return_value.first.return_value = user_instance

    mock_send_email.return_value = True
    response = client.post(
        "/api/auth/password/reset-request",
        json={"email": "testuser@example.com"},
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": None,
        "message": "Password reset email sent",
    }
    mock_add.assert_called_once()
    mock_commit.assert_called_once()
    mock_send_email.assert_called_once()


def test_request_password_reset_validation_error(client):
    with patch(
        "app.controllers.auth_controller.RequestPasswordResetSchema"
    ) as mock_schema:
        mock_schema.return_value.load.side_effect = ValidationError(
            {"email": ["Not a valid email address"]}
        )

        response = client.post(
            "/api/auth/password/reset-request",
            json={"email": "invalid-email"},
            headers={"Content-Type": "application/json"},
        )

        assert response.status_code == 400
        assert response.json == {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": {"email": ["Not a valid email address"]},
        }


def test_request_password_reset_email_not_found(mock_user_query, client):
    mock_user_query.filter_by.return_value.first.return_value = None
    response = client.post(
        "/api/auth/password/reset-request",
        json={"email": "unknown@example.com"},
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Email not found",
    }


def test_request_password_reset_email_failure(
    mock_user_query, mock_db_operations, mock_send_email, client
):
    mock_add, mock_commit = mock_db_operations
    user_instance = MagicMock()
    user_instance.email = "testuser@example.com"
    mock_user_query.filter_by.return_value.first.return_value = user_instance

    mock_send_email.side_effect = Exception("Email service error")
    response = client.post(
        "/api/auth/password/reset-request",
        json={"email": "testuser@example.com"},
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 500
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Failed to send email: Email service error",
    }
    mock_add.assert_called_once()
    mock_commit.assert_called()


def test_verify_reset_code_success(
    mock_reset_code_query, mock_verify_reset_code_schema, client
):
    mock_request_data = {"email": "testuser@example.com", "code": "123456"}
    mock_verify_reset_code_schema.return_value.load.return_value = mock_request_data

    reset_code_instance = MagicMock()
    reset_code_instance.created_at = datetime.utcnow() - timedelta(minutes=5)
    reset_code_instance.is_used = False
    mock_reset_code_query.filter_by.return_value.first.return_value = (
        reset_code_instance
    )
    response = client.post(
        "/api/auth/password/verify-reset-code",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": None,
        "message": "Code verified successfully",
    }


def test_verify_reset_code_validation_error(mock_verify_reset_code_schema, client):
    mock_verify_reset_code_schema.return_value.load.side_effect = ValidationError(
        {
            "email": ["Not a valid email address"],
            "code": ["Length must be between 6 and 6."],
        }
    )

    mock_request_data = {"email": "invalid-email", "code": "123"}
    response = client.post(
        "/api/auth/password/verify-reset-code",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {
            "email": ["Not a valid email address"],
            "code": ["Length must be between 6 and 6."],
        },
    }


def test_verify_reset_code_invalid_or_used_code(
    mock_reset_code_query, mock_verify_reset_code_schema, client
):
    mock_request_data = {"email": "testuser@example.com", "code": "123456"}
    mock_verify_reset_code_schema.return_value.load.return_value = mock_request_data

    mock_reset_code_query.filter_by.return_value.first.return_value = None
    response = client.post(
        "/api/auth/password/verify-reset-code",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Invalid or expired code",
    }


def test_verify_reset_code_expired(
    mock_reset_code_query, mock_verify_reset_code_schema, client
):
    mock_request_data = {"email": "testuser@example.com", "code": "123456"}
    mock_verify_reset_code_schema.return_value.load.return_value = mock_request_data

    reset_code_instance = MagicMock()
    reset_code_instance.created_at = datetime.utcnow() - timedelta(minutes=16)
    reset_code_instance.is_used = False
    mock_reset_code_query.filter_by.return_value.first.return_value = (
        reset_code_instance
    )
    response = client.post(
        "/api/auth/password/verify-reset-code",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 410
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Code expired",
    }


def test_reset_password_success(
    mock_reset_code_query,
    mock_user_query,
    mock_password_forgot_schema,
    mock_sqlalchemy,
    client,
):
    mock_request_data = {
        "email": "testuser@example.com",
        "code": "123456",
        "new_password": "newpassword123",
    }
    mock_password_forgot_schema.return_value.load.return_value = mock_request_data

    reset_code_instance = MagicMock()
    reset_code_instance.is_used = False
    reset_code_instance.created_at = datetime.utcnow() - timedelta(minutes=5)
    mock_reset_code_query.filter_by.return_value.first.return_value = (
        reset_code_instance
    )

    user_instance = MagicMock()
    user_instance.password_hash = "oldpasswordhash"
    mock_user_query.filter_by.return_value.first.return_value = user_instance
    response = client.post(
        "/api/auth/password/reset-password",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": None,
        "message": "Password reset successfully",
    }
    assert user_instance.password_hash != "oldpasswordhash"
    mock_sqlalchemy.session.commit.assert_called()


def test_reset_password_validation_error(mock_password_forgot_schema, client):
    mock_password_forgot_schema.return_value.load.side_effect = ValidationError(
        {
            "email": ["Not a valid email address"],
            "code": ["Length must be between 6 and 6."],
            "new_password": ["Length must be at least 6."],
        }
    )

    mock_request_data = {
        "email": "invalid-email",
        "code": "123",
        "new_password": "short",
    }
    response = client.post(
        "/api/auth/password/reset-password",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Validation failed",
        "errors": {
            "email": ["Not a valid email address"],
            "code": ["Length must be between 6 and 6."],
            "new_password": ["Length must be at least 6."],
        },
    }


def test_reset_password_invalid_code(
    mock_reset_code_query, mock_password_forgot_schema, client
):
    mock_request_data = {
        "email": "testuser@example.com",
        "code": "123456",
        "new_password": "newpassword123",
    }
    mock_password_forgot_schema.return_value.load.return_value = mock_request_data

    mock_reset_code_query.filter_by.return_value.first.return_value = None
    response = client.post(
        "/api/auth/password/reset-password",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 400
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "Invalid or expired code",
    }


def test_reset_password_user_not_found(
    mock_reset_code_query, mock_user_query, mock_password_forgot_schema, client
):
    mock_request_data = {
        "email": "testuser@example.com",
        "code": "123456",
        "new_password": "newpassword123",
    }
    mock_password_forgot_schema.return_value.load.return_value = mock_request_data

    reset_code_instance = MagicMock()
    reset_code_instance.is_used = False
    mock_reset_code_query.filter_by.return_value.first.return_value = (
        reset_code_instance
    )

    mock_user_query.filter_by.return_value.first.return_value = None
    response = client.post(
        "/api/auth/password/reset-password",
        json=mock_request_data,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "User not found",
    }


def test_get_user_info_success(
    mock_user_query, mock_jwt_required, mock_get_jwt_identity, client
):
    user_instance = MagicMock()
    user_instance.id = 1
    user_instance.username = "testuser"
    user_instance.email = "testuser@example.com"
    user_instance.preferences = "metric"
    mock_user_query.get.return_value = user_instance

    mock_get_jwt_identity.return_value = 1

    access_token = create_access_token(identity=1)
    response = client.get(
        "/api/auth/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {
            "id": 1,
            "username": "testuser",
            "email": "testuser@example.com",
            "preferences": "metric",
        },
        "message": "User information retrieved successfully",
    }


def test_get_user_info_user_not_found(
    mock_user_query, mock_jwt_required, mock_get_jwt_identity, client
):
    mock_user_query.get.return_value = None

    mock_get_jwt_identity.return_value = 999

    access_token = create_access_token(identity=999)
    response = client.get(
        "/api/auth/user",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "User not found",
    }


def test_delete_account_success(
    mock_user_query,
    mock_delete_jwt_required,
    mock_get_jwt_identity,
    mock_add_token_to_blacklist,
    mock_sqlalchemy,
    client,
):
    user_instance = MagicMock()
    user_instance.id = 1
    user_instance.username = "testuser"
    user_instance.email = "testuser@example.com"
    user_instance.preferences = "metric"
    mock_user_query.get.return_value = user_instance
    mock_get_jwt_identity.return_value = 1

    access_token = create_access_token(identity=1)
    response = client.delete(
        "/api/auth/delete",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": {
            "id": 1,
            "username": "testuser",
            "email": "testuser@example.com",
            "preferences": "metric",
        },
        "message": "User account deleted successfully",
    }
    mock_sqlalchemy.session.delete.assert_called_once_with(user_instance)
    mock_sqlalchemy.session.commit.assert_called()
    mock_add_token_to_blacklist.assert_called()


def test_delete_account_user_not_found(
    mock_user_query, mock_delete_jwt_required, mock_get_jwt_identity, client
):
    mock_user_query.get.return_value = None

    mock_get_jwt_identity.return_value = 999

    access_token = create_access_token(identity=999)
    response = client.delete(
        "/api/auth/delete",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "User not found",
    }


def test_logout_success(
    mock_delete_jwt_required, mock_logout_get_jwt, mock_add_token_to_blacklist, client
):
    expires_at = datetime.utcnow()
    mock_logout_get_jwt.return_value = {
        "jti": "some_jti",
        "exp": expires_at.timestamp(),
    }

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json == {
        "status": "success",
        "data": None,
        "message": "Successfully logged out",
    }
    actual_call = mock_add_token_to_blacklist.call_args[0]
    assert actual_call[0] == "some_jti"
    assert abs(
        actual_call[1] - datetime.fromtimestamp(mock_logout_get_jwt.return_value["exp"])
    ) < timedelta(milliseconds=10)


def test_logout_exception_handling(
    mock_delete_jwt_required, mock_logout_get_jwt, mock_add_token_to_blacklist, client
):
    mock_logout_get_jwt.return_value = {
        "jti": "some_jti",
        "exp": datetime.utcnow().timestamp(),
    }

    mock_add_token_to_blacklist.side_effect = Exception(
        "Mocked exception during logout"
    )

    access_token = create_access_token(identity=1)
    response = client.post(
        "/api/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 500
    assert response.json == {
        "status": "error",
        "data": None,
        "message": "An error occurred during logout",
        "errors": "Mocked exception during logout",
    }
