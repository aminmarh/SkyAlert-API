from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.models.database_model import FavoriteCity
from app.schemas.favorite_schema import AddFavoriteCitySchema, DeleteFavoriteCitySchema


@jwt_required()
def add_favorite_city():
    """
    Add a city to the user's favorite list.
    ---
    tags:
      - Favorite Cities
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            city:
              type: string
              description: City name
              example: Paris
    responses:
      201:
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                city:
                  type: string
                  example: Paris
            message:
              type: string
              example: City 'Paris' added to favorites
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
              example: {"city": ["City name must be a string containing only letters and spaces"]}
      409:
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
              example: City already in favorites
    """
    user_id = get_jwt_identity()
    data = request.json

    try:
        validated_data = AddFavoriteCitySchema().load(data)
    except ValidationError as err:
        return {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": err.messages,
        }, 400

    city = validated_data["city"]

    if FavoriteCity.query.filter_by(user_id=user_id, city=city).first():
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "City already in favorites",
                }
            ),
            409,
        )

    favorite = FavoriteCity(user_id=user_id, city=city)
    db.session.add(favorite)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {"city": city},
                "message": f"City '{city}' added to favorites",
            }
        ),
        201,
    )


@jwt_required()
def remove_favorite_city():
    """
    Remove a city from the user's favorite list.
    ---
    tags:
      - Favorite Cities
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            city:
              type: string
              description: City name
              example: Paris
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
                city:
                  type: string
                  example: Paris
            message:
              type: string
              example: City removed from favorites
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
              example: {"city": ["City name must be a string containing only letters and spaces"]}
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
              example: Favorite city not found
    """
    user_id = get_jwt_identity()
    data = request.json

    try:
        validated_data = DeleteFavoriteCitySchema().load(data)
    except ValidationError as err:
        return {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": err.messages,
        }, 400

    city = validated_data["city"]

    favorite = FavoriteCity.query.filter_by(user_id=user_id, city=city).first()
    if not favorite:
        return (
            jsonify(
                {"status": "error", "data": None, "message": "Favorite city not found"}
            ),
            404,
        )

    db.session.delete(favorite)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {"city": city},
                "message": "City removed from favorites",
            }
        ),
        200,
    )


@jwt_required()
def get_favorite_cities():
    """
    Get the user's list of favorite cities.
    ---
    tags:
      - Favorite Cities
    security:
      - Bearer: []
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  city:
                    type: string
                    example: Paris
            message:
              type: string
              example: List of favorite cities retrieved successfully
      401:
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
              example: "Unauthorized"
    """
    user_id = get_jwt_identity()

    favorites = FavoriteCity.query.filter_by(user_id=user_id).all()

    favorite_cities = [{"id": f.id, "city": f.city} for f in favorites]

    return (
        jsonify(
            {
                "status": "success",
                "data": favorite_cities,
                "message": "List of favorite cities retrieved successfully",
            }
        ),
        200,
    )
