from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow.exceptions import ValidationError

from app.helpers.weather_helper import WeatherAPI
from app.models.database_model import User
from app.schemas.weather_schema import WeatherRequestSchema, SearchLocationSchema


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
                  items:
                    type: object
                  description: List of current weather data
                forecast:
                  type: array
                  items:
                    type: object
                  description: List of forecast data
                location:
                  type: array
                  items:
                    type: object
                  description: List of location data
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
    if not user:
        return (
            jsonify({"status": "error", "data": None, "message": "User not found"}),
            404,
        )
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

    try:
        forecast = WeatherAPI.get_forecast(city, days, preferences)
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "An error occurred while retrieving the forecast",
                    "errors": str(e),
                }
            ),
            500,
        )

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


@jwt_required()
def search_location():
    """
    Recherche de localisation.
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
            query:
              type: string
              description: Name of the city
              default: Paris
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
                name:
                  type: string
                  example: Paris
                region:
                  type: string
                  example: Ile-de-France
                country:
                  type: string
                  example: France
                lat:
                  type: string
                  example: 48.85
                lon:
                  type: string
                  example: 2.35
                url:
                  type: string
                  example: paris-ile-de-france-france
            message:
              type: string
              example: Weather location search for Paris retrieved successfully
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
    """
    data = request.json

    try:
        validated_data = SearchLocationSchema().load(data)
    except ValidationError as err:
        return {
            "status": "error",
            "data": None,
            "message": "Validation failed",
            "errors": err.messages,
        }, 400

    query = validated_data["query"]

    try:
        city = WeatherAPI.location_search(query)
    except Exception as e:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "An error occurred while retrieving the location",
                    "errors": str(e),
                }
            ),
            500,
        )

    return (
        jsonify(
            {
                "status": "success",
                "data": city,
                "message": f"Weather location search for {query} retrieved successfully",
            }
        ),
        200,
    )
