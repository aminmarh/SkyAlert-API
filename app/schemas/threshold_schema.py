from marshmallow import Schema, fields, validate


class CityIDType(fields.Int):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.Range(
            min=1, error="City ID must be a positive integer"
        )
        super().__init__(
            *args, metadata={"description": "ID of the favorite city"}, **kwargs
        )


class ThresholdType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.OneOf(
            ["storm", "heatwave", "flood"], error="Invalid Threshold Type"
        )
        super().__init__(
            *args,
            metadata={
                "description": "Type of the Threshold (e.g., storm, heatwave, flood)"
            },
            **kwargs
        )


class PositiveIntType(fields.Int):
    def __init__(self, *args, **kwargs):
        metadata = kwargs.pop("metadata", {})  # Récupère les métadonnées sans conflit
        metadata["description"] = "Positive Int value"
        kwargs["metadata"] = metadata
        kwargs["validate"] = validate.Range(
            min=0, error="Value must be a positive number"
        )
        super().__init__(*args, **kwargs)


class StormSchema(Schema):
    favorite_city_id = CityIDType(required=True)
    gust_speed = PositiveIntType(
        required=True, metadata={"description": "Gust speed of the storm"}
    )
    wind_speed = PositiveIntType(
        required=True, metadata={"description": "Wind speed of the storm"}
    )


class HeatwaveSchema(Schema):
    favorite_city_id = CityIDType(required=True)
    temperature = PositiveIntType(
        required=True, metadata={"description": "Temperature during the heatwave"}
    )
    humidity = PositiveIntType(
        required=True, metadata={"description": "Humidity during the heatwave"}
    )


class FloodSchema(Schema):
    favorite_city_id = CityIDType(required=True)
    precipitation = PositiveIntType(
        required=True, metadata={"description": "Precipitation level during the flood"}
    )


class DeleteThresholdSchema(Schema):
    favorite_city_id = CityIDType(required=True)
    threshold_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Threshold ID must be a positive integer"),
        metadata={"description": "ID of the threshold"},
    )
    threshold_type = ThresholdType(required=True)


class GetThresholdSchema(Schema):
    favorite_city_id = CityIDType(required=True)
