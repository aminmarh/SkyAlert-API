import pytest

from unittest.mock import MagicMock, patch
from app.helpers.generic_helper import convert_units, create_notification


def test_convert_units_wind_speed_metric_to_imperial():
    result = convert_units(100, "metric", "imperial", "wind_speed")
    assert result == 62  # 100 km/h -> ~62 mph


def test_convert_units_wind_speed_imperial_to_metric():
    result = convert_units(62, "imperial", "metric", "wind_speed")
    assert result == 100  # ~62 mph -> 100 km/h


def test_convert_units_temperature_metric_to_imperial():
    result = convert_units(0, "metric", "imperial", "temperature")
    assert result == 32  # 0°C -> 32°F


def test_convert_units_temperature_imperial_to_metric():
    result = convert_units(32, "imperial", "metric", "temperature")
    assert result == 0  # 32°F -> 0°C


def test_convert_units_precipitation_metric_to_imperial():
    result = convert_units(25, "metric", "imperial", "precipitation")
    assert result == 1  # 25 mm -> ~1 inch


def test_convert_units_precipitation_imperial_to_metric():
    result = convert_units(1, "imperial", "metric", "precipitation")
    assert result == 25  # ~1 inch -> 25 mm


def test_convert_units_no_conversion_needed():
    result = convert_units(10, "metric", "metric", "wind_speed")
    assert result == 10  # No conversion, just rounding


def test_convert_units_invalid_unit_type():
    with pytest.raises(ValueError) as excinfo:
        convert_units(10, "metric", "imperial", "invalid_type")
    assert "Unsupported conversion from metric to imperial for invalid_type" in str(
        excinfo.value
    )


def test_convert_units_invalid_from_to_units():
    with pytest.raises(ValueError) as excinfo:
        convert_units(10, "invalid", "imperial", "wind_speed")
    assert "Unsupported conversion from invalid to imperial for wind_speed" in str(
        excinfo.value
    )


@patch("app.helpers.generic_helper.db")
def test_create_notification_success(mock_db):
    mock_db.session.add = MagicMock()
    mock_db.session.commit = MagicMock()

    create_notification(user_id=1, title="Test Title", message="Test Message")

    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()


@patch("app.helpers.generic_helper.db")
def test_create_notification_db_exception(mock_db):
    mock_db.session.add.side_effect = Exception("DB Error")

    with pytest.raises(Exception) as excinfo:
        create_notification(user_id=1, title="Test Title", message="Test Message")

    assert "DB Error" in str(excinfo.value)
