from marshmallow import Schema, fields, validate


class StormSchema(Schema):
    favorite_city_id = fields.Int(required=True, description="ID of the favorite city")
    gust_speed = fields.Float(
        required=True, validate=[validate.Range(min=0)], description="Gust speed"
    )
    wind_speed = fields.Float(
        required=True, validate=[validate.Range(min=0)], description="Wind speed"
    )


class HeatwaveSchema(Schema):
    favorite_city_id = fields.Int(required=True, description="ID of the favorite city")
    temperature = fields.Float(
        required=True, validate=[validate.Range(min=0)], description="Temperature"
    )
    humidity = fields.Float(
        required=True, validate=[validate.Range(min=0)], description="Humidity"
    )


class FloodSchema(Schema):
    favorite_city_id = fields.Int(required=True, description="ID of the favorite city")
    precipitation = fields.Float(
        required=True, validate=[validate.Range(min=0)], description="Precipitation"
    )


class DeleteThresholdSchema(Schema):
    favorite_city_id = fields.Int(required=True, description="ID of the favorite city")
    threshold_id = fields.Int(required=True, description="ID of the favorite city")
    threshold_type = fields.Str(
        required=True,
        validate=[
            validate.OneOf(
                ["storm", "heatwave", "flood"], error="Invalid Threshold Type"
            ),
        ],
        description="Type of the Threshold",
    )


class GetThresholdSchema(Schema):
    favorite_city_id = fields.Int(required=True, description="ID of the favorite city")
