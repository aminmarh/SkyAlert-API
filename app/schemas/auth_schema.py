from marshmallow import Schema, fields, validate


class RegisterSchema(Schema):
    username = fields.Str(
        required=True,
        validate=validate.Regexp(
            r"^[a-zA-Z\s]+$",
            error="Username must be a string containing only letters and spaces",
        ),
        description="Username of the user",
    )
    email = fields.Email(required=True, description="Email address of the user")
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6),
            validate.Regexp(
                r"^[^\s"
                r"\U0001F600-\U0001F64F"
                r"\U0001F300-\U0001F5FF"
                r"\U0001F680-\U0001F6FF"
                r"\U0001F700-\U0001F77F"
                r"\U0001F780-\U0001F7FF"
                r"\U0001F800-\U0001F8FF"
                r"\U0001F900-\U0001F9FF"
                r"\U0001FA00-\U0001FA6F"
                r"\U0001FA70-\U0001FAFF]+$",
                error="Password must not contain spaces",
            ),
        ],
        description="Password of the user",
    )


class LoginSchema(Schema):
    email = fields.Email(required=True, description="Email address used for login")
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6),
            validate.Regexp(
                r"^[^\s"
                r"\U0001F600-\U0001F64F"
                r"\U0001F300-\U0001F5FF"
                r"\U0001F680-\U0001F6FF"
                r"\U0001F700-\U0001F77F"
                r"\U0001F780-\U0001F7FF"
                r"\U0001F800-\U0001F8FF"
                r"\U0001F900-\U0001F9FF"
                r"\U0001FA00-\U0001FA6F"
                r"\U0001FA70-\U0001FAFF]+$",
                error="Password must not contain spaces",
            ),
        ],
        description="Password used for login",
    )


class UserUpdateSchema(Schema):
    username = fields.Str(
        validate=validate.Regexp(
            r"^[a-zA-Z\s]+$",
            error="Username must be a string containing only letters and spaces",
        ),
        description="Updated username",
    )
    email = fields.Email(description="Updated email address")


class PasswordUpdateSchema(Schema):
    current_password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6),
            validate.Regexp(
                r"^[^\s"
                r"\U0001F600-\U0001F64F"
                r"\U0001F300-\U0001F5FF"
                r"\U0001F680-\U0001F6FF"
                r"\U0001F700-\U0001F77F"
                r"\U0001F780-\U0001F7FF"
                r"\U0001F800-\U0001F8FF"
                r"\U0001F900-\U0001F9FF"
                r"\U0001FA00-\U0001FA6F"
                r"\U0001FA70-\U0001FAFF]+$",
                error="Password must not contain spaces",
            ),
        ],
        description="Current password of the user",
    )
    new_password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6),
            validate.Regexp(
                r"^[^\s"
                r"\U0001F600-\U0001F64F"
                r"\U0001F300-\U0001F5FF"
                r"\U0001F680-\U0001F6FF"
                r"\U0001F700-\U0001F77F"
                r"\U0001F780-\U0001F7FF"
                r"\U0001F800-\U0001F8FF"
                r"\U0001F900-\U0001F9FF"
                r"\U0001FA00-\U0001FA6F"
                r"\U0001FA70-\U0001FAFF]+$",
                error="Password must not contain spaces",
            ),
        ],
        description="New password of the user",
    )


class RequestPasswordResetSchema(Schema):
    email = fields.Email(required=True, description="Email address of the user")


class VerifyResetCodeSchema(Schema):
    email = fields.Email(required=True, description="Email address of the user")
    code = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6, max=6),
            validate.Regexp(
                r"^\d+$", error="Code must contain only digits and no spaces"
            ),
        ],
        description="Code sent to the user's email",
    )


class PasswordForgotSchema(Schema):
    email = fields.Email(required=True, description="Email address of the user")
    code = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6, max=6),
            validate.Regexp(
                r"^\d+$", error="Code must contain only digits and no spaces"
            ),
        ],
        description="Code sent to the user's email",
    )
    new_password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=6),
        ],
        description="New password of the user",
    )
