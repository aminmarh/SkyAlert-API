from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.helpers.weather import WeatherAPI
from app.models.user import User


@jwt_required()
def get_forecast():
    """
    Weather forecast for a city.
    ---
    tags:
      - Weather
    security:
      - Bearer: []
    parameters:
      - name: city
        in: query
        required: true
        type: string
        description: Name of the city
        default: Paris
        example: Paris
      - name: days
        in: query
        required: true
        type: integer
        description: Number of days of weather forecast. Value ranges from 1 to 14
        default: 1
        example: 5
      - name: aqi
        in: query
        required: false
        type: string
        description: Enable/Disable Air Quality data in forecast API output. Example, aqi=yes or aqi=no.
        default: "no"
        example: aqui
      - name: alerts
        in: query
        required: false
        type: string
        description: Enable/Disable alerts in forecast API output. Example, alerts=yes or alerts=no.
        default: "no"
        example: alerts
    responses:
      200:
        description: Weather forecast data
      400:
        description: Missing city parameter
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    preferences = user.preferences if user else "metric"

    city = request.args.get("city")
    days = request.args.get("days", 3)
    aqi = request.args.get("aqi", "no")
    alerts = request.args.get("alerts", "no")

    if not city:
        return jsonify({"error": "City parameter is required"}), 400

    forecast_data = WeatherAPI.get_forecast(city, days, aqi, alerts, preferences)

    if "error" in forecast_data:
        return jsonify({"error": forecast_data["error"]}), 400

    return jsonify(forecast_data)
