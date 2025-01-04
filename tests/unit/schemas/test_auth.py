import pytest

from marshmallow.exceptions import ValidationError
from app.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    VerifyEmailCodeSchema,
    UserUpdateSchema,
    PasswordUpdateSchema,
    RequestPasswordResetSchema,
    VerifyPasswordResetCodeSchema,
    PasswordForgotSchema,
)


def test_register_schema_success():
    valid_data = {
        "username": "John Doe",
        "email": "john.doe@example.com",
        "password": "SecureP@ss123",
    }
    schema = RegisterSchema()
    result = schema.load(valid_data)
    assert result["username"] == "John Doe"
    assert result["email"] == "john.doe@example.com"
    assert result["password"] == "SecureP@ss123"


def test_register_schema_error_username_invalid_format():
    invalid_data = {
        "username": "John123",
        "email": "john.doe@example.com",
        "password": "SecureP@ss123",
    }
    schema = RegisterSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Username must be a string containing only letters and spaces" in str(
        excinfo.value
    )


def test_register_schema_error_email_invalid_format():
    invalid_data = {
        "username": "John Doe",
        "email": "invalid-email",
        "password": "SecureP@ss123",
    }
    schema = RegisterSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Not a valid email address." in str(excinfo.value)


def test_register_schema_error_password_too_short():
    invalid_data = {
        "username": "John Doe",
        "email": "john.doe@example.com",
        "password": "short",
    }
    schema = RegisterSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Password must be at least 6 characters long" in str(excinfo.value)


def test_register_schema_error_password_invalid_characters():
    invalid_data = {
        "username": "John Doe",
        "email": "john.doe@example.com",
        "password": "Invalid🙂Pass",
    }
    schema = RegisterSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Password must not contain spaces or emojis" in str(excinfo.value)


def test_login_schema_success():
    valid_data = {"email": "john.doe@example.com", "password": "SecureP@ss123"}
    schema = LoginSchema()
    result = schema.load(valid_data)
    assert result["email"] == "john.doe@example.com"
    assert result["password"] == "SecureP@ss123"


def test_login_schema_error_missing_email():
    invalid_data = {"password": "SecureP@ss123"}
    schema = LoginSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_login_schema_error_email_invalid_format():
    invalid_data = {
        "email": "invalid-email",
        "password": "SecureP@ss123",
    }
    schema = LoginSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Not a valid email address." in str(excinfo.value)


def test_login_schema_error_password_missing():
    invalid_data = {"email": "john.doe@example.com"}
    schema = LoginSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_verify_email_code_schema_success():
    valid_data = {
        "username": "John Doe",
        "email": "john.doe@example.com",
        "password": "SecureP@ss123",
        "code": "123456",
    }
    schema = VerifyEmailCodeSchema()
    result = schema.load(valid_data)
    assert result["username"] == "John Doe"
    assert result["email"] == "john.doe@example.com"
    assert result["password"] == "SecureP@ss123"
    assert result["code"] == "123456"


def test_verify_email_code_schema_error_code_invalid_format():
    invalid_data = {
        "username": "John Doe",
        "email": "john.doe@example.com",
        "password": "SecureP@ss123",
        "code": "ABCDEF",
    }
    schema = VerifyEmailCodeSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Code must contain only digits" in str(excinfo.value)


def test_verify_email_code_schema_error_code_length():
    invalid_data = {
        "username": "John Doe",
        "email": "john.doe@example.com",
        "password": "SecureP@ss123",
        "code": "12345",
    }
    schema = VerifyEmailCodeSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Code must be 6 digits long" in str(excinfo.value)


def test_user_update_schema_success():
    valid_data = {
        "username": "Jane Doe",
        "preferences": "metric",
    }
    schema = UserUpdateSchema()
    result = schema.load(valid_data)
    assert result["username"] == "Jane Doe"
    assert result["preferences"] == "metric"


def test_user_update_schema_error_invalid_preferences():
    invalid_data = {
        "username": "Jane Doe",
        "preferences": "unknown",
    }
    schema = UserUpdateSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Preferences must be either 'metric' or 'imperial'" in str(excinfo.value)


def test_password_update_schema_success():
    valid_data = {
        "current_password": "OldPass123",
        "new_password": "NewPass123",
    }
    schema = PasswordUpdateSchema()
    result = schema.load(valid_data)
    assert result["current_password"] == "OldPass123"
    assert result["new_password"] == "NewPass123"


def test_password_update_schema_error_password_invalid_format():
    invalid_data = {
        "current_password": "OldPass123",
        "new_password": "short",
    }
    schema = PasswordUpdateSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Password must be at least 6 characters long" in str(excinfo.value)


def test_request_password_reset_schema_success():
    valid_data = {"email": "john.doe@example.com"}
    schema = RequestPasswordResetSchema()
    result = schema.load(valid_data)
    assert result["email"] == "john.doe@example.com"


def test_request_password_reset_schema_error_email_invalid_format():
    invalid_data = {"email": "invalid-email"}
    schema = RequestPasswordResetSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Not a valid email address." in str(excinfo.value)


def test_verify_password_reset_code_schema_success():
    valid_data = {
        "email": "john.doe@example.com",
        "code": "123456",
    }
    schema = VerifyPasswordResetCodeSchema()
    result = schema.load(valid_data)
    assert result["email"] == "john.doe@example.com"
    assert result["code"] == "123456"


def test_verify_password_reset_code_schema_error_code_invalid_format():
    invalid_data = {
        "email": "john.doe@example.com",
        "code": "ABCDEF",
    }
    schema = VerifyPasswordResetCodeSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Code must contain only digits" in str(excinfo.value)


def test_verify_password_reset_code_schema_error_code_length():
    invalid_data = {
        "email": "john.doe@example.com",
        "code": "12345",
    }
    schema = VerifyPasswordResetCodeSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Code must be 6 digits long" in str(excinfo.value)


def test_password_forgot_schema_success():
    valid_data = {
        "email": "john.doe@example.com",
        "code": "123456",
        "new_password": "NewPass123",
    }
    schema = PasswordForgotSchema()
    result = schema.load(valid_data)
    assert result["email"] == "john.doe@example.com"
    assert result["code"] == "123456"
    assert result["new_password"] == "NewPass123"


def test_password_forgot_schema_error_email_invalid_format():
    invalid_data = {
        "email": "invalid-email",
        "code": "123456",
        "new_password": "NewPass123",
    }
    schema = PasswordForgotSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Not a valid email address." in str(excinfo.value)


def test_password_forgot_schema_error_code_invalid_format():
    invalid_data = {
        "email": "john.doe@example.com",
        "code": "ABCDEF",
        "new_password": "NewPass123",
    }
    schema = PasswordForgotSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Code must contain only digits" in str(excinfo.value)


def test_password_forgot_schema_error_code_length():
    invalid_data = {
        "email": "john.doe@example.com",
        "code": "12345",
        "new_password": "NewPass123",
    }
    schema = PasswordForgotSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Code must be 6 digits long" in str(excinfo.value)


def test_password_forgot_schema_error_password_invalid_format():
    invalid_data = {
        "email": "john.doe@example.com",
        "code": "123456",
        "new_password": "short",
    }
    schema = PasswordForgotSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Password must be at least 6 characters long" in str(excinfo.value)
