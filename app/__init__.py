import logging

from flask import Flask, request
from flask_cors import CORS
from flasgger import Swagger

from app.extensions import db, jwt, migrate
from app.routes import init_routes
from app.config import Config
from app.scheduler import start_scheduler


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    swagger_config = {
        "headers": [
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Headers", "Content-Type,Authorization"),
            ("Access-Control-Allow-Methods", "GET,POST,DELETE,PUT,OPTIONS"),
        ],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/apispec.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'",
            }
        },
        "security": [{"Bearer": []}],
    }

    template = {
        "swagger": "2.0",
        "info": {
            "title": "SkyAlert API",
            "description": "API for SkyAlert application",
            "version": "0.0.1",
        },
    }

    Swagger(app, template=template, config=swagger_config)

    logging.basicConfig(level=app.config["LOG_LEVEL"])
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
    app.logger.addHandler(logger)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    init_routes(app)

    with app.app_context():

        @app.after_request
        def start_scheduler_after_login(response):
            if request.endpoint == "auth.login" and response.status_code == 200:
                app.logger.info("User logged in successfully. Starting scheduler...")
                start_scheduler(app)
            return response

    return app
