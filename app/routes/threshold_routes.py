from flask import Blueprint
from app.controllers.threshold_controller import (
    create_storm_threshold,
    create_flood_threshold,
    create_heatwave_threshold,
    delete_threshold,
    get_thresholds,
)

threshold_bp = Blueprint("threshold", __name__)

threshold_bp.add_url_rule("/storm", view_func=create_storm_threshold, methods=["POST"])
threshold_bp.add_url_rule("/flood", view_func=create_flood_threshold, methods=["POST"])
threshold_bp.add_url_rule(
    "/heatwave", view_func=create_heatwave_threshold, methods=["POST"]
)
threshold_bp.add_url_rule("/delete", view_func=delete_threshold, methods=["DELETE"])
threshold_bp.add_url_rule("", view_func=get_thresholds, methods=["POST"])
