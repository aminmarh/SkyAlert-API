from marshmallow import Schema, fields, validate


class UsernameType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.Regexp(
            r"^[a-zA-Z\s]+$",
            error="Username must be a string containing only letters and spaces",
        )
        super().__init__(
            *args, metadata={"description": "Username of the user"}, **kwargs
        )


class PasswordType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = [
            validate.Length(min=6, error="Password must be at least 6 characters long"),
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
                error="Password must not contain spaces or emojis",
            ),
        ]
        super().__init__(
            *args, metadata={"description": "Password of the user"}, **kwargs
        )


class EmailType(fields.Email):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, metadata={"description": "Email address of the user"}, **kwargs
        )


class CodeType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = [
            validate.Length(min=6, max=6, error="Code must be 6 digits long"),
            validate.Regexp(r"^\d+$", error="Code must contain only digits"),
        ]
        super().__init__(
            *args,
            metadata={"description": "Verification code sent to the user"},
            **kwargs
        )


class PreferencesType(fields.Str):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.OneOf(
            ["metric", "imperial"],
            error="Preferences must be either 'metric' or 'imperial'",
        )
        super().__init__(
            *args,
            metadata={
                "description": "User preferences for measurement units (metric or imperial)"
            },
            **kwargs
        )


class RegisterSchema(Schema):
    username = UsernameType(required=True)
    email = EmailType(required=True)
    password = PasswordType(required=True)


class LoginSchema(Schema):
    email = EmailType(required=True)
    password = PasswordType(required=True)


class VerifyEmailCodeSchema(Schema):
    username = UsernameType(required=True)
    email = EmailType(required=True)
    password = PasswordType(required=True)
    code = CodeType(required=True)


class UserUpdateSchema(Schema):
    username = UsernameType(required=False)
    email = EmailType(required=False)
    preferences = PreferencesType(required=True)


class PasswordUpdateSchema(Schema):
    current_password = PasswordType(required=True)
    new_password = PasswordType(required=True)


class RequestPasswordResetSchema(Schema):
    email = EmailType(required=True)


class VerifyPasswordResetCodeSchema(Schema):
    email = EmailType(required=True)
    code = CodeType(required=True)


class PasswordForgotSchema(Schema):
    email = EmailType(required=True)
    code = CodeType(required=True)
    new_password = PasswordType(required=True)
