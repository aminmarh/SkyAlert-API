import pytest

from marshmallow.exceptions import ValidationError
from app.schemas.favorite_schema import AddFavoriteCitySchema, DeleteFavoriteCitySchema


def test_add_favorite_city_schema_success():
    valid_data = {"city": "Paris"}
    schema = AddFavoriteCitySchema()
    result = schema.load(valid_data)
    assert result["city"] == "Paris"


def test_add_favorite_city_schema_error_city_contains_numbers():
    invalid_data = {"city": "Paris123"}
    schema = AddFavoriteCitySchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "City name must be a string containing only letters and spaces" in str(
        excinfo.value
    )


def test_add_favorite_city_schema_error_city_missing():
    invalid_data = {}
    schema = AddFavoriteCitySchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)


def test_delete_favorite_city_schema_success():
    valid_data = {"city": "Tokyo"}
    schema = DeleteFavoriteCitySchema()
    result = schema.load(valid_data)
    assert result["city"] == "Tokyo"


def test_delete_favorite_city_schema_error_city_contains_numbers():
    invalid_data = {"city": "Berlin123"}
    schema = DeleteFavoriteCitySchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "City name must be a string containing only letters and spaces" in str(
        excinfo.value
    )


def test_delete_favorite_city_schema_error_city_missing():
    invalid_data = {}
    schema = DeleteFavoriteCitySchema()
    with pytest.raises(ValidationError) as excinfo:
        schema.load(invalid_data)
    assert "Missing data for required field." in str(excinfo.value)
