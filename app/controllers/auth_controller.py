import random
import datetime

from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from marshmallow import ValidationError
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, add_token_to_blacklist
from app.helpers.email_helper import Email
from app.models.database_model import User, ResetCode
from app.schemas.auth_schema import (
    RegisterSchema,
    LoginSchema,
    UserUpdateSchema,
    PasswordUpdateSchema,
    RequestPasswordResetSchema,
    VerifyPasswordResetCodeSchema,
    PasswordForgotSchema,
    VerifyEmailCodeSchema,
)


def register():
    """
    Inscrire un nouvel utilisateur.
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: testuser
            email:
              type: string
              example: testuser@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Verification email sent successfully"
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Validation failed"
            errors:
              type: object
              example: {"password": ["Length must be at least 6."]}
      409:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Email already registered"
      500:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Failed to send email: Error details here"
    """
    data = request.json

    try:
        validated_data = RegisterSchema().load(data)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Validation failed",
                    "errors": err.messages,
                }
            ),
            400,
        )

    username = validated_data["username"]
    email = validated_data["email"]

    if User.query.filter_by(email=email).first():
        return (
            jsonify(
                {"status": "error", "data": None, "message": "Email already registered"}
            ),
            409,
        )

    code = f"{random.randint(100000, 999999)}"

    reset_code = ResetCode(email=email, code=code, is_used=False)
    db.session.add(reset_code)
    db.session.commit()

    email_body = (
        f"Bonjour {username},\n\n"
        "Merci de vous être inscrit sur SkyAlert !\n"
        "Veuillez utiliser le code ci-dessous pour vérifier votre adresse email et compléter votre inscription :\n"
        f"{code}\n"
        "Si vous n’avez pas demandé cette inscription, veuillez ignorer cet email.\n"
        "Pour votre sécurité, ce code expirera dans 15 minutes.\n\n"
        "Ceci est un e-mail automatique, veuillez ne pas y répondre.\n\n"
        "Cordialement,\n"
        "L'équipe SkyAlert"
    )

    try:
        Email.send_email(
            to=email,
            subject="SkyAlert - Code de vérification de votre email",
            body=email_body,
        )
    except Exception as e:
        db.session.delete(reset_code)
        db.session.commit()
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": f"Failed to send email: {str(e)}",
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "status": "success",
                "data": None,
                "message": "Verification email sent successfully",
            }
        ),
        201,
    )


def verif_mail():
    """
    Vérifier un code de validation d'email.
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              example: testuser
            email:
              type: string
              example: testuser@example.com
            password:
              type: string
              example: password123
            code:
              type: string
              description: The 6-digit reset code
              example: "123456"
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              properties:
                username:
                  type: string
                  example: "testuser"
                email:
                  type: string
                  example: "testuser@example.com"
            message:
              type: string
              example: "User registered successfully"
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Validation failed"
            errors:
              type: object
              example: {"email": ["Not a valid email address"],
                "code": ["Length must be between 6 and 6."]}
      401:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Invalid or expired code"
      410:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Code expired"
    """
    data = request.json

    try:
        validated_data = VerifyEmailCodeSchema().load(data)
    except ValidationError as err:
        return {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": err.messages,
        }, 400

    username = validated_data["username"]
    email = validated_data["email"]
    password = validated_data["password"]
    code = validated_data["code"]

    reset_code = ResetCode.query.filter_by(
        email=email, code=code, is_used=False
    ).first()
    if not reset_code:
        return (
            jsonify(
                {"status": "error", "data": None, "message": "Invalid or expired code"}
            ),
            401,
        )

    time_elapsed = datetime.datetime.utcnow() - reset_code.created_at
    if time_elapsed.total_seconds() > 900:
        return (
            jsonify({"status": "error", "data": None, "message": "Code expired"}),
            410,
        )

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    reset_code.is_used = True
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {"username": username, "email": email},
                "message": "User registered successfully",
            }
        ),
        200,
    )


def login():
    """
    Connexion d'un utilisateur
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              example: testuser@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                access_token:
                  type: string
                  example: "eyJhbGciOiJIUzI1Ni..."
                username:
                  type: string
                  example: "testuser"
            message:
              type: string
              example: "Login successful"
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Validation failed"
            errors:
              type: object
              example: {"email": ["Not a valid email address"]}
      401:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Invalid credentials"
    """
    data = request.json

    try:
        validated_data = LoginSchema().load(data)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Validation failed",
                    "errors": err.messages,
                }
            ),
            400,
        )

    email = validated_data["email"]
    password = validated_data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return (
            jsonify(
                {"status": "error", "data": None, "message": "Invalid credentials"}
            ),
            401,
        )

    access_token = create_access_token(identity=str(user.id), expires_delta=None)

    return (
        jsonify(
            {
                "status": "success",
                "data": {"access_token": access_token, "username": user.username},
                "message": "Login successful",
            }
        ),
        200,
    )


@jwt_required()
def logout():
    """
    Déconnexion de l'utilisateur
    ---
    tags:
      - Authentification
    security:
      - Bearer: []
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Logged out successfully"
      500:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "An error occurred during logout"
            errors:
              type: string
              example: "Error details here"
    """
    try:
        jti = get_jwt()["jti"]
        expires_at = datetime.datetime.fromtimestamp(get_jwt()["exp"])
        add_token_to_blacklist(jti, expires_at)

        return (
            jsonify(
                {
                    "status": "success",
                    "data": None,
                    "message": "Successfully logged out",
                }
            ),
            200,
        )
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "An error occurred during logout",
                    "errors": str(e),
                }
            ),
            500,
        )


@jwt_required()
def update_user():
    """
    Mis à jour des informations de l'utilisateur
    ---
    tags:
      - Authentification
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
              description: New username
              example: new_username
            email:
              type: string
              description: New email address
              example: new_email@example.com
            preferences:
              type: string
              description: User preferences for units (metric or imperial)
              example: metric
    responses:
      200:
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User information updated successfully"
            user:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: "new_username"
                email:
                  type: string
                  example: "new_email@example.com"
                preferences:
                  type: string
                  example: "metric"
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Validation failed"
            errors:
              type: object
              example: {"email": ["Not a valid email address"]}
      404:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "User not found"
      409:
        schema:
          type: object
          properties:
            status:
                type: string
                example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Email already taken"
    """
    user_id = get_jwt_identity()
    data = request.json

    try:
        validated_data = UserUpdateSchema().load(data)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Validation failed",
                    "errors": err.messages,
                }
            ),
            400,
        )

    user = User.query.get(user_id)
    if not user:
        return (
            jsonify({"status": "error", "data": None, "message": "User not found"}),
            404,
        )

    changes_detected = False

    if "username" in validated_data and validated_data["username"] != user.username:
        user.username = validated_data["username"]
        changes_detected = True

    if (
        "preferences" in validated_data
        and validated_data["preferences"] != user.preferences
    ):
        user.preferences = validated_data["preferences"]
        changes_detected = True

    if "email" in validated_data and validated_data["email"] != user.email:
        # Check if email is already in use
        if User.query.filter(
            User.email == validated_data["email"], User.id != user_id
        ).first():
            return (
                jsonify(
                    {"status": "error", "data": None, "message": "Email already taken"}
                ),
                409,
            )
        user.email = validated_data["email"]
        changes_detected = True

    if not changes_detected:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "No changes detected",
                }
            ),
            400,
        )

    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "preferences": user.preferences,
                    }
                },
                "message": "User updated successfully",
            }
        ),
        200,
    )


@jwt_required()
def update_password():
    """
    Mettre à jour le mot de passe de l'utilisateur.
    ---
    tags:
      - Authentification
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            current_password:
              type: string
              description: Current user password
              example: "current_password_example"
            new_password:
              type: string
              description: New User Password
              example: "new_password_example"
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Password updated successfully"
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Validation failed"
            errors:
              type: object
              example: {"new_password": ["Shorter than minimum length 6"]}
      401:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Current password is incorrect"
    """
    user_id = get_jwt_identity()
    data = request.json

    try:
        validated_data = PasswordUpdateSchema().load(data)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Validation failed",
                    "errors": err.messages,
                }
            ),
            400,
        )

    current_password = validated_data["current_password"]
    new_password = validated_data["new_password"]

    user = User.query.get(user_id)
    if not user or not check_password_hash(user.password_hash, current_password):
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Current password is incorrect",
                }
            ),
            401,
        )

    user.set_password(new_password)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": None,
                "message": "Password updated successfully",
            }
        ),
        200,
    )


def request_password_reset():
    """
    Demander un code de réinitialisation de mot de passe.
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              description: User's email address
              example: "testuser@example.com"
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Password reset email sent"
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Validation failed"
            errors:
              type: object
              example: {"email": ["Not a valid email address"]}
      404:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Email not found"
      500:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Failed to send email: Error details here"
    """
    data = request.json

    try:
        validated_data = RequestPasswordResetSchema().load(data)
    except ValidationError as err:
        return {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": err.messages,
        }, 400

    email = validated_data["email"]

    user = User.query.filter_by(email=email).first()
    if not user:
        return (
            jsonify({"status": "error", "data": None, "message": "Email not found"}),
            404,
        )

    code = f"{random.randint(100000, 999999)}"

    reset_code = ResetCode(email=email, code=code)
    db.session.add(reset_code)
    db.session.commit()

    email_body = (
        "Bonjour,\n\n"
        "Vous avez demandé une réinitialisation de votre mot de passe pour votre compte SkyAlert.\n"
        "Si vous êtes bien à l'origine de cette demande,"
        "votre code de réinitialisation de mot de passe est :\n"
        f"{code}\n"
        "Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer ce message.\n"
        "Pour votre sécurité, ce code expirera dans 15 minutes.\n\n"
        "Ceci est un e-mail automatique, veuillez ne pas y répondre.\n\n"
        "Cordialement,\n"
        "L'équipe SkyAlert"
    )

    try:
        Email.send_email(
            to=email,
            subject="SkyAlert - Demande de réinitialisation de mot de passe",
            body=email_body,
        )
    except Exception as e:
        db.session.delete(reset_code)
        db.session.commit()
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": f"Failed to send email: {str(e)}",
                }
            ),
            500,
        )

    return (
        jsonify(
            {"status": "success", "data": None, "message": "Password reset email sent"}
        ),
        200,
    )


def verify_reset_code():
    """
    Vérifier un code de réinitialisation de mot de passe.
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              description: The email of the user who received the code
              example: "testuser@example.com"
            code:
              type: string
              description: The 6-digit reset code
              example: "123456"
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Code verified successfully"
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Validation failed"
            errors:
              type: object
              example: {"email": ["Not a valid email address"], "code": ["Length must be between 6 and 6."]}
      401:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Invalid or expired code"
      410:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Code expired"
    """
    data = request.json

    try:
        validated_data = VerifyPasswordResetCodeSchema().load(data)
    except ValidationError as err:
        return {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": err.messages,
        }, 400

    code = validated_data["code"]
    email = validated_data["email"]

    reset_code = ResetCode.query.filter_by(
        email=email, code=code, is_used=False
    ).first()

    if not reset_code:
        return (
            jsonify(
                {"status": "error", "data": None, "message": "Invalid or expired code"}
            ),
            401,
        )

    time_elapsed = datetime.datetime.utcnow() - reset_code.created_at
    if time_elapsed.total_seconds() > 900:
        return (
            jsonify({"status": "error", "data": None, "message": "Code expired"}),
            410,
        )

    return (
        jsonify(
            {"status": "success", "data": None, "message": "Code verified successfully"}
        ),
        200,
    )


def reset_password():
    """
    Réinitialiser le mot de passe d'un utilisateur.
    ---
    tags:
      - Authentification
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
              description: The email of the user who requested the reset
              example: "testuser@example.com"
            code:
              type: string
              description: The 6-digit reset code
              example: "123456"
            new_password:
              type: string
              description: The user's new password
              example: "newpassword123"
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Password reset successfully"
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Validation failed"
            errors:
              type: object
              example: {"email": ["Not a valid email address"],
                "code": ["Length must be between 6 and 6."],
                "new_password": ["Length must be at least 6."]}
      401:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "Invalid or expired code"
      404:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "User not found"
    """
    data = request.json

    try:
        validated_data = PasswordForgotSchema().load(data)
    except ValidationError as err:
        return {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": err.messages,
        }, 400

    code = validated_data["code"]
    email = validated_data["email"]
    new_password = validated_data["new_password"]

    reset_code = ResetCode.query.filter_by(
        email=email, code=code, is_used=False
    ).first()
    if not reset_code:
        return (
            jsonify(
                {"status": "error", "data": None, "message": "Invalid or expired code"}
            ),
            401,
        )

    user = User.query.filter_by(email=email).first()
    if not user:
        return (
            jsonify({"status": "error", "data": None, "message": "User not found"}),
            404,
        )

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    reset_code.is_used = True
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": None,
                "message": "Password reset successfully",
            }
        ),
        200,
    )


@jwt_required()
def get_user_info():
    """
    Information de l'utilisateur
    ---
    tags:
      - Authentification
    security:
      - Bearer: []
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: "testuser"
                email:
                  type: string
                  example: "testuser@example.com"
                preferences:
                  type: string
                  example: "metric"
            message:
              type: string
              example: "User information retrieved successfully"
      404:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "User not found"
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return (
            jsonify({"status": "error", "data": None, "message": "User not found"}),
            404,
        )

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "preferences": user.preferences,
                },
                "message": "User information retrieved successfully",
            }
        ),
        200,
    )


@jwt_required()
def delete_account():
    """
    Supprimer le compte utilisateur.
    ---
    tags:
      - Authentification
    security:
      - Bearer: []
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            data:
              type: object
              properties:
                id:
                  type: integer
                  example: 1
                username:
                  type: string
                  example: "testuser"
                email:
                  type: string
                  example: "testuser@example.com"
                preferences:
                  type: string
                  example: "metric"
            message:
              type: string
              example: "User account deleted successfully"
      404:
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            data:
              type: object
              example: null
            message:
              type: string
              example: "User not found"
    """
    user_id = get_jwt_identity()

    user = User.query.get(user_id)
    if not user:
        return (
            jsonify({"status": "error", "data": None, "message": "User not found"}),
            404,
        )

    jti = get_jwt()["jti"]
    expires_at = datetime.datetime.fromtimestamp(get_jwt()["exp"])
    add_token_to_blacklist(jti, expires_at)

    db.session.delete(user)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "preferences": user.preferences,
                },
                "message": "User account deleted successfully",
            }
        ),
        200,
    )
