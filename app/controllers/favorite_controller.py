from flask import jsonify, request

from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import FavoriteCity
from app.extensions import db


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
        description: City added to favorites
      400:
        description: Missing parameter
      401:
        description: Unauthorized user
    """
    user_id = get_jwt_identity()
    data = request.json

    city = data.get("city")

    if not city or not isinstance(city, str):
        return jsonify({"error": "City is required"}), 400

    if FavoriteCity.query.filter_by(user_id=user_id, city=city).first():
        return jsonify({"error": "City already in favorites"}), 400

    favorite = FavoriteCity(user_id=user_id, city=city)
    db.session.add(favorite)
    db.session.commit()

    return jsonify({"message": f"City '{city}' added to favorites"}), 201


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
        description: City removed from favorites
      400:
        description: Missing parameter
      401:
        description: Unauthorized user
    """
    user_id = get_jwt_identity()
    data = request.json
    city = data.get("city")

    if not city:
        return jsonify({"error": "City is required"}), 400

    favorite = FavoriteCity.query.filter_by(user_id=user_id, city=city).first()

    if not favorite:
        return jsonify({"error": "Favorite city not found"}), 404

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"message": "City removed from favorites", "city": city}), 200


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
        description: List of favorite cities
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
                description: Favorite city ID
                example: 1
              city:
                type: string
                description: City name
                example: Paris
      401:
        description: Missing or invalid authorization token
    """
    user_id = get_jwt_identity()
    favorites = FavoriteCity.query.filter_by(user_id=user_id).all()

    return jsonify([{"id": f.id, "city": f.city} for f in favorites])
