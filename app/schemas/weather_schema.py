from marshmallow import Schema, fields, validate, post_load


class CityNameType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = [
            validate.Regexp(
                r".*",
                error=(
                    "City must contain only letters, numbers, spaces, or valid geographical symbols (-, +, .). "
                    "Special characters are not allowed."
                ),
            )
        ]
        super().__init__(
            *args,
            metadata={
                "description": (
                    "Name of the city (letters, numbers, and spaces only) or geographical coordinates "
                    "in the format 'latitude longitude' (e.g., '48.8566 2.3522'). Special characters are not allowed."
                )
            },
            **kwargs
        )


class PositiveIntType(fields.Int):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.OneOf(
            [1, 2, 3],
            error="Days must be either 1, 2 or 3",
        )
        super().__init__(
            *args, metadata={"description": "Positive int value"}, **kwargs
        )


class WeatherRequestSchema(Schema):
    city = CityNameType(required=True)
    days = PositiveIntType(required=True)


class SearchLocationSchema(Schema):
    query = CityNameType(required=True)


class ConditionSchema(Schema):
    code = fields.Int(required=True)
    icon = fields.Str(required=True)
    text = fields.Str(required=True)


class CurrentWeatherSchema(Schema):
    last_updated = fields.Str(required=True)
    temp_c = fields.Float(required=True)
    temp_f = fields.Float(required=True)
    is_day = fields.Int(required=True)
    condition = fields.Nested(ConditionSchema, required=True)
    wind_kph = fields.Float(required=True)
    wind_mph = fields.Float(required=True)
    wind_dir = fields.Str(required=True)
    precip_mm = fields.Float(required=True)
    precip_in = fields.Float(required=True)
    humidity = fields.Int(required=True)
    feelslike_c = fields.Float(required=True)
    feelslike_f = fields.Float(required=True)
    vis_km = fields.Float(required=True)
    vis_miles = fields.Float(required=True)
    gust_kph = fields.Float(required=True)
    gust_mph = fields.Float(required=True)


class DayWeatherSchema(Schema):
    maxtemp_c = fields.Float(required=True)
    maxtemp_f = fields.Float(required=True)
    mintemp_c = fields.Float(required=True)
    mintemp_f = fields.Float(required=True)
    avgtemp_c = fields.Float(required=True)
    avgtemp_f = fields.Float(required=True)
    totalprecip_mm = fields.Float(required=True)
    totalprecip_in = fields.Float(required=True)
    condition = fields.Nested(ConditionSchema, required=True)


class HourlyWeatherSchema(Schema):
    time = fields.Str(required=True)
    temp_c = fields.Float(required=True)
    temp_f = fields.Float(required=True)
    is_day = fields.Int(required=True)
    condition = fields.Nested(ConditionSchema, required=True)
    wind_kph = fields.Float(required=True)
    wind_mph = fields.Float(required=True)
    wind_dir = fields.Str(required=True)
    precip_mm = fields.Float(required=True)
    precip_in = fields.Float(required=True)
    humidity = fields.Int(required=True)
    feelslike_c = fields.Float(required=True)
    feelslike_f = fields.Float(required=True)
    vis_km = fields.Float(required=True)
    vis_miles = fields.Float(required=True)
    gust_kph = fields.Float(required=True)
    gust_mph = fields.Float(required=True)


class DailyWeatherSchema(Schema):
    date = fields.Str(required=True)
    day = fields.Nested(DayWeatherSchema, required=True)
    hour = fields.List(fields.Nested(HourlyWeatherSchema))


class ForecastSchema(Schema):
    forecastday = fields.List(fields.Nested(DailyWeatherSchema), required=True)


class LocationSchema(Schema):
    name = fields.Str(required=True)
    region = fields.Str(required=True)
    country = fields.Str(required=True)
    lat = fields.Float(required=True)
    lon = fields.Float(required=True)
    tz_id = fields.Str(required=True)
    localtime_epoch = fields.Int(required=True)
    localtime = fields.Str(required=True)


class WeatherResponseSchema(Schema):
    system = "metric"
    location = fields.Nested(LocationSchema, required=True)
    current = fields.Nested(CurrentWeatherSchema, required=True)
    forecast = fields.Nested(ForecastSchema, required=True)

    @post_load
    def filter_units(self, data, many=None, **kwargs):
        """
        Filtre les champs pour correspondre au système de mesure (metric ou imperial).
        """
        system = self.system

        metric_fields = {
            "temp_c",
            "wind_kph",
            "precip_mm",
            "feelslike_c",
            "vis_km",
            "gust_kph",
            "maxtemp_c",
            "mintemp_c",
            "avgtemp_c",
            "totalprecip_mm",
        }

        imperial_fields = {
            "temp_f",
            "wind_mph",
            "precip_in",
            "feelslike_f",
            "vis_miles",
            "gust_mph",
            "maxtemp_f",
            "mintemp_f",
            "avgtemp_f",
            "totalprecip_in",
        }

        universal_fields = [
            "last_updated",
            "is_day",
            "condition",
            "wind_dir",
            "humidity",
            "date",
            "time",
        ]

        def filter_data(obj):
            fields_to_keep = metric_fields if system == "metric" else imperial_fields
            fields_to_keep.update(universal_fields)
            for key in list(obj.keys()):
                if key not in fields_to_keep:
                    obj.pop(key, None)
                elif isinstance(obj[key], float):
                    obj[key] = round(obj[key])

        if "current" in data:
            filter_data(data["current"])
        if "forecast" in data and "forecastday" in data["forecast"]:
            for day in data["forecast"]["forecastday"]:
                if "day" in day:
                    filter_data(day["day"])
                if "hour" in day and isinstance(day["hour"], list):
                    for hour in day["hour"]:
                        filter_data(hour)

        return data
