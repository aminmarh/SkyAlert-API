from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    from app.controllers.auth_controller import blacklist_tokens

    jti = jwt_payload["jti"]
    return jti in blacklist_tokens
