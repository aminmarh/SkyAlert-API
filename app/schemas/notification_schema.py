from marshmallow import Schema, fields, validate


class NotificationIDType(fields.Int):
    def __init__(self, *args, **kwargs):
        kwargs["validate"] = validate.Range(
            min=1, error="Notification ID must be a positive integer"
        )
        super().__init__(
            *args, metadata={"description": "ID of the notification"}, **kwargs
        )


class MarkAsReadSchema(Schema):
    notification_id = NotificationIDType(required=True)


class DeleteNotificationSchema(Schema):
    notification_id = NotificationIDType(required=True)
