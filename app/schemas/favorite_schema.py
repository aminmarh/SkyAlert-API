from marshmallow import Schema, fields, validate


class AddFavoriteCitySchema(Schema):
    city = fields.Str(
        required=True,
        validate=[
            validate.Regexp(
                r"^[a-zA-Z\s]+$",
                error="City name must be a string containing only letters and spaces",
            )
        ],
        description="Name of the city",
    )


class DeleteFavoriteCitySchema(Schema):
    city = fields.Str(
        required=True,
        validate=[
            validate.Regexp(
                r"^[a-zA-Z\s]+$",
                error="City name must be a string containing only letters and spaces",
            )
        ],
        description="Name of the city",
    )
