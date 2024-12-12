from flask import Blueprint

from app.controllers.auth_controller import (
    login,
    logout,
    register,
    update_user,
    update_password,
    request_password_reset,
    reset_password,
)

auth_bp = Blueprint("auth", __name__)

auth_bp.add_url_rule("/login", view_func=login, methods=["POST"])
auth_bp.add_url_rule("/register", view_func=register, methods=["POST"])
auth_bp.add_url_rule("/user", view_func=update_user, methods=["PUT"])
auth_bp.add_url_rule("/password/update", view_func=update_password, methods=["PUT"])
auth_bp.add_url_rule(
    "/password/reset-request", view_func=request_password_reset, methods=["POST"]
)
auth_bp.add_url_rule(
    "/password/reset/<token>", view_func=reset_password, methods=["POST"]
)
auth_bp.add_url_rule("/logout", view_func=logout, methods=["POST"])
