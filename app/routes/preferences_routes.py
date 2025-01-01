from flask import Blueprint

from app.controllers.preferences_controller import update_preferences

preferences_bp = Blueprint("preferences", __name__)

preferences_bp.add_url_rule("/update", view_func=update_preferences, methods=["PUT"])
