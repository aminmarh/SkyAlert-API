from app.routes.auth_routes import auth_bp


def init_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
