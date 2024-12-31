from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def add_token_to_blacklist(jti, expires_at):
    from app.models.user import TokenBlocklist

    token = TokenBlocklist(jti=jti, expires_at=expires_at)
    db.session.add(token)
    db.session.commit()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    from app.models.user import TokenBlocklist

    jti = jwt_payload["jti"]
    return TokenBlocklist.query.filter_by(jti=jti).first() is not None
