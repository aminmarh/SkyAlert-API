from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.user import User
from app.schemas.preferences_schema import PreferencesSchema


@jwt_required()
def update_preferences():
    """
    Mise à jour des préférences de l'utilisateur
    ---
    tags:
        - Preferences
    security:
        - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            preferences:
                type: string
                enum: ["metric", "imperial"]
                example: "metric"
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                preferences:
                  type: string
                  example: "metric"
            message:
              type: string
              example: Preferences updated successfully
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            data:
              type: object
              example: null
            message:
              type: string
              example: Validation failed
            errors:
              type: object
              example: {"preferences": ["Invalid Preferences Type"]}
      404:
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            data:
              type: object
              example: null
            message:
              type: string
              example: User not found
    """
    user_id = get_jwt_identity()
    data = request.json

    try:
        validated_data = PreferencesSchema().load(data)
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

    preferences = validated_data["preferences"]

    user = User.query.get(user_id)
    if not user:
        return (
            jsonify({"status": "error", "data": None, "message": "User not found"}),
            404,
        )

    user.preferences = preferences
    db.session.commit()

    return jsonify(
        {
            "status": "success",
            "data": {"preferences": preferences},
            "message": "Preferences updated successfully",
        }
    )
