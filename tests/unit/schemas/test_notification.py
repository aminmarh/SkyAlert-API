import pytest

from marshmallow.exceptions import ValidationError
from app.schemas.notification_schema import MarkAsReadSchema, DeleteNotificationSchema


def test_mark_as_read_schema_success():
    valid_data = {"notification_id": 42}
    schema = MarkAsReadSchema()
    result = schema.load(valid_data)
    assert result["notification_id"] == 42


def test_mark_as_read_schema_error_notification_id_negative():
    invalid_data = {"notification_id": -5}
    schema = MarkAsReadSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Notification ID must be a positive integer" in str(excinfo.value)


def test_mark_as_read_schema_error_notification_id_zero():
    invalid_data = {"notification_id": 0}
    schema = MarkAsReadSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Notification ID must be a positive integer" in str(excinfo.value)


def test_mark_as_read_schema_error_notification_id_missing():
    invalid_data = {}
    schema = MarkAsReadSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_delete_notification_schema_success():
    valid_data = {"notification_id": 100}
    schema = DeleteNotificationSchema()
    result = schema.load(valid_data)
    assert result["notification_id"] == 100


def test_delete_notification_schema_error_notification_id_negative():
    invalid_data = {"notification_id": -10}
    schema = DeleteNotificationSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Notification ID must be a positive integer" in str(excinfo.value)


def test_delete_notification_schema_error_notification_id_zero():
    invalid_data = {"notification_id": 0}
    schema = DeleteNotificationSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Notification ID must be a positive integer" in str(excinfo.value)


def test_delete_notification_schema_error_notification_id_missing():
    invalid_data = {}
    schema = DeleteNotificationSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)
