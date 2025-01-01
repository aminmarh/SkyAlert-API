from app.routes.auth_routes import auth_bp
from app.routes.weather_routes import weather_bp
from app.routes.favorite_routes import favorite_bp
from app.routes.threshold_routes import threshold_bp
from app.routes.preferences_routes import preferences_bp


def init_routes(app):
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(weather_bp, url_prefix="/api/weather")
    app.register_blueprint(favorite_bp, url_prefix="/api/favorites")
    app.register_blueprint(threshold_bp, url_prefix="/api/thresholds")
    app.register_blueprint(preferences_bp, url_prefix="/api/preferences")
