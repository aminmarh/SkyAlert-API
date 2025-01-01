from marshmallow import Schema, fields, validate


class CityNameType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = [
            validate.Regexp(
                r"^[a-zA-Z0-9\s\.\-\+]+$",
                error=(
                    "City must contain only letters, numbers, spaces, or valid geographical symbols (-, +, .). "
                    "Special characters are not allowed."
                ),
            )
        ]
        kwargs["description"] = (
            "Name of the city (letters, numbers, and spaces only) or geographical coordinates "
            "in the format 'latitude longitude' (e.g., '48.8566 2.3522'). Special characters are not allowed."
        )
        super().__init__(*args, **kwargs)


class PositiveIntType(fields.Int):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.OneOf(
            [1, 2, 3],
            error="Days must be either 1, 2 or 3",
        )
        kwargs["description"] = kwargs.get("description", "Positive int value")
        super().__init__(*args, **kwargs)


class WeatherRequestSchema(Schema):
    city = CityNameType(required=True)
    days = PositiveIntType(required=True)


class SearchLocationSchema(Schema):
    query = CityNameType(required=True)
