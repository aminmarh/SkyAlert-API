from flask import Blueprint
from app.controllers.favorite_controller import (
    add_favorite_city,
    remove_favorite_city,
    get_favorite_cities,
)

favorite_bp = Blueprint("favorite", __name__)

favorite_bp.add_url_rule("", view_func=get_favorite_cities, methods=["GET"])
favorite_bp.add_url_rule("/add", view_func=add_favorite_city, methods=["POST"])
favorite_bp.add_url_rule("/delete", view_func=remove_favorite_city, methods=["DELETE"])
