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

from app.models.user import User, PasswordResetCode
from app.extensions import db
from app.helpers.email import Email
from app.schemas.user_schema import (
    RegisterSchema,
    LoginSchema,
    UserUpdateSchema,
    PasswordUpdateSchema,
)


def register():
    """
    Register a new user
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
        description: User successfully registered
      400:
        description: Validation error
    """
    data = request.json

    try:
        validated_data = RegisterSchema().load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    username = validated_data["username"]
    email = validated_data["email"]
    password = validated_data["password"]

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


def login():
    """
    Logging in a user
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
        description: Successful login
        schema:
          type: object
          properties:
            access_token:
              type: string
              example: "eyJhbGciOiJIUzI1Ni..."
            username:
              type: string
              example: "testuser"
      401:
        description: Identifiants invalides
    """
    data = request.json

    try:
        validated_data = LoginSchema().load(data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    email = validated_data["email"]
    password = validated_data["password"]

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id), expires_delta=None)

    return jsonify({"access_token": access_token, "username": user.username}), 200


blacklist_tokens = set()


@jwt_required()
def logout():
    """
    Log out a user
    ---
    tags:
      - Authentification
    security:
      - Bearer: []
    responses:
      200:
        description: Logout successful
        schema:
          type: object
          properties:
            message:
              type: string
              example: Successfully logged out
    """
    jti = get_jwt()["jti"]
    blacklist_tokens.add(jti)
    return jsonify({"message": "Successfully logged out"}), 200


@jwt_required()
def update_user():
    """
    Updating user information
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
    responses:
      200:
        description: Update successful
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
      400:
        description: Validation error or invalid data provided
        schema:
          type: object
          properties:
            error:
              type: object
              example: {"username": ["This field must be between 3 and 80 characters"]}
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
      401:
        description: Not Authorized - Missing or Invalid Token
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing or invalid token"
      409:
        description: Conflict - Username or email already in use
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Username already taken"
    """
    user_id = get_jwt_identity()
    data = request.json
    schema = UserUpdateSchema()

    try:
        validated_data = schema.load(data)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if "username" in validated_data:
        if User.query.filter(
            User.username == validated_data["username"], User.id != user_id
        ).first():
            return jsonify({"error": "Username already taken"}), 400
        user.username = validated_data["username"]

    if "email" in validated_data:
        if User.query.filter(
            User.email == validated_data["email"], User.id != user_id
        ).first():
            return jsonify({"error": "Email already in use"}), 400
        user.email = validated_data["email"]

    db.session.commit()
    return (
        jsonify(
            {"message": "User information updated successfully", "user": user.to_dict()}
        ),
        200,
    )


@jwt_required()
def update_password():
    """
    Update user password
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
        description: Password updated successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: Password updated successfully
      400:
        description: Missing or invalid parameters
        schema:
          type: object
          properties:
            error:
              type: string
              example: Current and new passwords are required
      401:
        description: Current password incorrect or user not authorized
        schema:
          type: object
          properties:
            error:
              type: string
              example: Current password is incorrect
    """
    user_id = get_jwt_identity()
    password_update_schema = PasswordUpdateSchema()

    try:
        data = password_update_schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": err.messages}), 400

    current_password = data.get("current_password")
    new_password = data.get("new_password")

    user = User.query.get(user_id)
    if not user or not check_password_hash(user.password_hash, current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    user.set_password(new_password)
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200


password_reset_tokens = {}


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
        description: Reset code sent successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Reset code sent successfully"
      404:
        description: Email does not exist in the database
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Email not found"
      500:
        description: Error sending email
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Failed to send email: SMTP Error"
    """
    data = request.json
    email = data.get("email")
    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    code = f"{random.randint(100000, 999999)}"

    reset_code = PasswordResetCode(email=email, code=code)
    db.session.add(reset_code)
    db.session.commit()

    email_body = (
        "Bonjour,\n\n"
        "Vous avez demandé une réinitialisation de votre mot de passe pour votre compte SkyAlert.\n"
        "Si vous êtes bien à l'origine de cette demande,"
        "votre code de réinitialisation de mot de passe est :\n"
        f"{code}\n"
        "Si vous n'avez pas demandé cette réinitialisation, veuillez ignorer ce message.\n"
        "Pour votre sécurité, ce lien expirera dans 15 minutes.\n\n"
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
        return jsonify({"error": f"Failed to send email: {str(e)}"}), 500

    return jsonify({"message": "Password reset email sent"}), 200


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
        description: Code verified successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Code verified successfully"
      400:
        description: Invalid or expired code
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or expired code"
    """
    data = request.json
    email = data.get("email")
    code = data.get("code")

    reset_code = PasswordResetCode.query.filter_by(
        email=email, code=code, is_used=False
    ).first()
    if not reset_code:
        return jsonify({"error": "Invalid or expired code"}), 400

    time_elapsed = datetime.datetime.utcnow() - reset_code.created_at
    if time_elapsed.total_seconds() > 900:
        return jsonify({"error": "Code expired"}), 400

    return jsonify({"message": "Code verified successfully"}), 200


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
        description: Password reset successfully
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Password reset successfully"
      400:
        description: Invalid or expired code
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Invalid or expired code"
      404:
        description: User not found
        schema:
          type: object
          properties:
            error:
              type: string
              example: "User not found"
    """
    data = request.json
    email = data.get("email")
    code = data.get("code")
    new_password = data.get("new_password")

    reset_code = PasswordResetCode.query.filter_by(
        email=email, code=code, is_used=False
    ).first()
    if not reset_code:
        return jsonify({"error": "Invalid or expired code"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.password_hash = generate_password_hash(new_password)
    db.session.commit()

    reset_code.is_used = True
    db.session.commit()

    return jsonify({"message": "Password reset successfully"}), 200
