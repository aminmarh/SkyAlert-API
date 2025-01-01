from marshmallow import Schema, fields, validate


class PreferencesType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.OneOf(
            ["metric", "imperial"],
            error="Preferences must be either 'metric' or 'imperial'",
        )
        kwargs["description"] = (
            "User preferences for measurement units (metric or imperial)"
        )
        super().__init__(*args, **kwargs)


class PreferencesSchema(Schema):
    preferences = PreferencesType(required=True)
