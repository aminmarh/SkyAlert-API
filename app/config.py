import os

from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///weather_app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwtsecret")
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "your_weather_api_key")
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access"]
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    SCHEDULER_API_ENABLED = os.getenv("SCHEDULER_API_ENABLED", True)
    EMAIL_SENDER = os.getenv("EMAIL_SENDER", "default_sender@example.com")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "default_password")
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.example.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
