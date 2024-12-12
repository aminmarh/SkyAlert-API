from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))


class UserUpdateSchema(Schema):
    username = fields.Str(validate=validate.Length(min=3, max=80))
    email = fields.Email()


class PasswordUpdateSchema(Schema):
    current_password = fields.Str(
        required=True,
        validate=validate.Length(min=6),
        description="Current user password",
    )
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=6),
        description="New User Password",
    )
