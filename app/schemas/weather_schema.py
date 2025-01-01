from marshmallow import Schema, fields, validate


class CityNameType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = [
            validate.Regexp(
                r"^[a-zA-Z\s]+$",
                error="City name must be a string containing only letters and spaces",
            )
        ]
        kwargs["description"] = "Name of the city"
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
