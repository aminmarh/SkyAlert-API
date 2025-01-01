from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow.exceptions import ValidationError

from app.helpers.weather import WeatherAPI
from app.models.user import User
from app.schemas.weather_schema import WeatherRequestSchema


@jwt_required()
def get_forecast():
    """
    Météo pour une ville.
    ---
    tags:
      - Weather
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
              description: Name of the city
              default: Paris
              example: Paris
            days:
              type: integer
              description: Number of days of weather forecast. Value ranges from 1 to 3
              default: 1
              example: 3
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
                current:
                  type: array
                forecast:
                  type: array
                location:
                  type: array
            message:
              type: string
              example: Weather forecast for Paris retrieved successfully
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
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    preferences = user.preferences if user else "metric"

    data = request.json

    try:
        validated_data = WeatherRequestSchema().load(data)
    except ValidationError as err:
        return {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": err.messages,
        }, 400

    city = validated_data["city"]
    days = validated_data["days"]

    forecast = WeatherAPI.get_forecast(city, days, preferences)

    return (
        jsonify(
            {
                "status": "success",
                "data": forecast,
                "message": f"Weather forecast for {city} retrieved successfully",
            }
        ),
        200,
    )
