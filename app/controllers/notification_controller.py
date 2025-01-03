from flask import jsonify, request
from marshmallow import ValidationError
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)

from app.extensions import db
from app.models.user import User, Notification
from app.schemas.notification_schema import MarkAsReadSchema, DeleteNotificationSchema


@jwt_required()
def get_notifications():
    """
    Récupérer les notifications d'un utilisateur.
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    responses:
      200:
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                    example: 1
                  title:
                    type: string
                    example: Flood threshold met for Paris
                  message:
                    type: string
                    example: "User's precipitation threshold: 10 mm - Actual: 10 mm"
                  is_read:
                    type: boolean
                    example: false
                  created_at:
                    type: string
                    example: "2024-01-01T12:00:00"
    """
    user_id = get_jwt_identity()
    notifications = (
        Notification.query.filter_by(user_id=user_id)
        .order_by(Notification.created_at.desc())
        .all()
    )

    result = [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "is_read": n.is_read,
            "created_at": n.created_at.isoformat(),
        }
        for n in notifications
    ]

    return (
        jsonify(
            {
                "status": "success",
                "data": result,
                "message": "Notifications retrieved successfully",
            }
        ),
        200,
    )


@jwt_required()
def mark_notification_as_read():
    """
    Marquer une notification comme lue.
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            notification_id:
              type: integer
              example: 1
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
                notification_id:
                  type: integer
                  example: 1
                is_read:
                  type: boolean
                  example: true
            message:
              type: string
              example: Notification marked as read successfully
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            data:
              type: object
              example: null
            message:
              type: string
              example: Validation failed
            errors:
              type: object
              example: {"notification_id": ["Not a valid number"]}
      404:
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            data:
              type: object
              example: null
            message:
              type: string
              example: Notification not found
    """
    data = request.json
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    try:
        validated_data = MarkAsReadSchema().load(data)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Validation failed",
                    "errors": err.messages,
                }
            ),
            400,
        )

    if not user:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "User not found",
                }
            ),
            404,
        )

    notification_id = validated_data["notification_id"]

    notification = Notification.query.filter_by(
        id=notification_id, user_id=user_id
    ).first()

    if not notification:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Notification not found",
                }
            ),
            404,
        )

    notification.is_read = True
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "notification_id": notification_id,
                    "is_read": notification.is_read,
                },
                "message": "Notification marked as read successfully",
            }
        ),
        200,
    )


@jwt_required()
def delete_notification():
    """
    Supprimer une notification.
    ---
    tags:
      - Notifications
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            notification_id:
              type: integer
              example: 1
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
                notification_id:
                  type: integer
                  example: 1
            message:
              type: string
              example: Notification deleted successfully
      400:
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            data:
              type: object
              example: null
            message:
              type: string
              example: Validation failed
            errors:
              type: object
              example: {"notification_id": ["Not a valid number"]}
      404:
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            data:
              type: object
              example: null
            message:
              type: string
              example: Notification not found
    """
    data = request.json
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    try:
        validated_data = DeleteNotificationSchema().load(data)
    except ValidationError as err:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Validation failed",
                    "errors": err.messages,
                }
            ),
            400,
        )

    if not user:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "User not found",
                }
            ),
            404,
        )

    notification_id = validated_data["notification_id"]

    notification = Notification.query.filter_by(
        id=notification_id, user_id=user_id
    ).first()

    if not notification:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Notification not found",
                }
            ),
            404,
        )

    db.session.delete(notification)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "notification_id": notification_id,
                },
                "message": "Notification deleted successfully",
            }
        ),
        200,
    )
