from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import logging

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def add_token_to_blacklist(jti, expires_at):
    from app.models.database_model import TokenBlocklist

    token = TokenBlocklist(jti=jti, expires_at=expires_at)
    db.session.add(token)
    db.session.commit()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    from app.models.database_model import TokenBlocklist

    jti = jwt_payload["jti"]
    return TokenBlocklist.query.filter_by(jti=jti).first() is not None


@jwt.invalid_token_loader
def invalid_token_callback(error):
    return (
        jsonify(
            {
                "status": "error",
                "data": None,
                "message": "Invalid token",
                "code": "INVALID_TOKEN",
            }
        ),
        401,
    )


@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    logging.warning("Expired token callback triggered.")
    return (
        jsonify(
            {
                "status": "error",
                "data": None,
                "message": "Session expired",
                "code": "TOKEN_EXPIRED",
            }
        ),
        401,
    )
