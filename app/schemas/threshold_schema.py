from marshmallow import Schema, fields, validate


class CityIDType(fields.Int):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.Range(
            min=1, error="City ID must be a positive integer"
        )
        kwargs["description"] = "ID of the favorite city"
        super().__init__(*args, **kwargs)


class ThresholdType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.OneOf(
            ["storm", "heatwave", "flood"], error="Invalid Threshold Type"
        )
        kwargs["description"] = "Type of the Threshold (e.g., storm, heatwave, flood)"
        super().__init__(*args, **kwargs)


class PositiveIntType(fields.Int):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.Range(
            min=0, error="Value must be a positive number"
        )
        kwargs["description"] = kwargs.get("description", "Positive Int value")
        super().__init__(*args, **kwargs)


class StormSchema(Schema):
    favorite_city_id = CityIDType(required=True)
    gust_speed = PositiveIntType(required=True, description="Gust speed of the storm")
    wind_speed = PositiveIntType(required=True, description="Wind speed of the storm")


class HeatwaveSchema(Schema):
    favorite_city_id = CityIDType(required=True)
    temperature = PositiveIntType(
        required=True, description="Temperature during the heatwave"
    )
    humidity = PositiveIntType(
        required=True, description="Humidity during the heatwave"
    )


class FloodSchema(Schema):
    favorite_city_id = CityIDType(required=True)
    precipitation = PositiveIntType(
        required=True, description="Precipitation level during the flood"
    )


class DeleteThresholdSchema(Schema):
    favorite_city_id = CityIDType(required=True)
    threshold_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Threshold ID must be a positive integer"),
        description="ID of the threshold",
    )
    threshold_type = ThresholdType(required=True)


class GetThresholdSchema(Schema):
    favorite_city_id = CityIDType(required=True)
