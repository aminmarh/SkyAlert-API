from flask import Blueprint
from app.controllers.notification_controller import (
    get_notifications,
    mark_notification_as_read,
    delete_notification,
)

notification_bp = Blueprint("notification", __name__)

notification_bp.add_url_rule("", view_func=get_notifications, methods=["GET"])
notification_bp.add_url_rule(
    "/mark-read", view_func=mark_notification_as_read, methods=["PUT"]
)
notification_bp.add_url_rule(
    "/delete", view_func=delete_notification, methods=["DELETE"]
)
