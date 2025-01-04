import pytest
from marshmallow.exceptions import ValidationError
from app.schemas.threshold_schema import (
    StormSchema,
    HeatwaveSchema,
    FloodSchema,
    DeleteThresholdSchema,
    GetThresholdSchema,
)


def test_storm_schema_success():
    valid_data = {"favorite_city_id": 1, "gust_speed": 50, "wind_speed": 30}
    schema = StormSchema()
    result = schema.load(valid_data)
    assert result["favorite_city_id"] == 1
    assert result["gust_speed"] == 50
    assert result["wind_speed"] == 30


def test_storm_schema_error_negative_gust_speed():
    invalid_data = {
        "favorite_city_id": 1,
        "gust_speed": -10,
        "wind_speed": 30,
    }
    schema = StormSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Value must be a positive number" in str(excinfo.value)


def test_storm_schema_error_missing_field():
    invalid_data = {"favorite_city_id": 1, "gust_speed": 50}
    schema = StormSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_heatwave_schema_success():
    valid_data = {"favorite_city_id": 2, "temperature": 40, "humidity": 70}
    schema = HeatwaveSchema()
    result = schema.load(valid_data)
    assert result["favorite_city_id"] == 2
    assert result["temperature"] == 40
    assert result["humidity"] == 70


def test_heatwave_schema_error_negative_temperature():
    invalid_data = {
        "favorite_city_id": 2,
        "temperature": -5,
        "humidity": 70,
    }
    schema = HeatwaveSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Value must be a positive number" in str(excinfo.value)


def test_flood_schema_success():
    valid_data = {"favorite_city_id": 3, "precipitation": 100}
    schema = FloodSchema()
    result = schema.load(valid_data)
    assert result["favorite_city_id"] == 3
    assert result["precipitation"] == 100


def test_flood_schema_error_negative_precipitation():
    invalid_data = {
        "favorite_city_id": 3,
        "precipitation": -20,
    }
    schema = FloodSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Value must be a positive number" in str(excinfo.value)


def test_delete_threshold_schema_success():
    valid_data = {"favorite_city_id": 1, "threshold_id": 5, "threshold_type": "storm"}
    schema = DeleteThresholdSchema()
    result = schema.load(valid_data)
    assert result["favorite_city_id"] == 1
    assert result["threshold_id"] == 5
    assert result["threshold_type"] == "storm"


def test_delete_threshold_schema_error_invalid_threshold_type():
    invalid_data = {
        "favorite_city_id": 1,
        "threshold_id": 5,
        "threshold_type": "invalid",
    }
    schema = DeleteThresholdSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Invalid Threshold Type" in str(excinfo.value)


def test_get_threshold_schema_success():
    valid_data = {"favorite_city_id": 1}
    schema = GetThresholdSchema()
    result = schema.load(valid_data)
    assert result["favorite_city_id"] == 1


def test_get_threshold_schema_error_negative_city_id():
    invalid_data = {"favorite_city_id": -1}
    schema = GetThresholdSchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "City ID must be a positive integer" in str(excinfo.value)
