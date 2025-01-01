from flask import Blueprint
from app.controllers.weather_controller import (
    get_forecast,
    search_location,
)

weather_bp = Blueprint("weather", __name__)

weather_bp.add_url_rule("/forecast", view_func=get_forecast, methods=["POST"])
weather_bp.add_url_rule("/search", view_func=search_location, methods=["POST"])
