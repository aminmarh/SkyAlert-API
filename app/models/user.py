import datetime

from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    preferences = db.Column(db.String(20), default="metric")

    favorites = db.relationship(
        "FavoriteCity",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    notification = db.relationship(
        "Notification",
        backref="user",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "preferences": self.preferences,
        }


class FavoriteCity(db.Model):
    __tablename__ = "favorite_city"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    city = db.Column(db.String(100), nullable=False)

    storm_thresholds = db.relationship(
        "StormThreshold",
        backref="favorite_city",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    heatwave_thresholds = db.relationship(
        "HeatwaveThreshold",
        backref="favorite_city",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    flood_thresholds = db.relationship(
        "FloodThreshold",
        backref="favorite_city",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class ResetCode(db.Model):
    __tablename__ = "reset_code"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(6), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    is_used = db.Column(db.Boolean, default=False)


class StormThreshold(db.Model):
    __tablename__ = "storm_threshold"

    id = db.Column(db.Integer, primary_key=True)
    favorite_city_id = db.Column(
        db.Integer, db.ForeignKey("favorite_city.id"), nullable=False
    )
    wind_speed_metric = db.Column(db.Float, nullable=False)
    wind_speed_imperial = db.Column(db.Float, nullable=False)
    gust_speed_metric = db.Column(db.Float, nullable=False)
    gust_speed_imperial = db.Column(db.Float, nullable=False)
    threshold_reached = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class HeatwaveThreshold(db.Model):
    __tablename__ = "heatwave_threshold"

    id = db.Column(db.Integer, primary_key=True)
    favorite_city_id = db.Column(
        db.Integer, db.ForeignKey("favorite_city.id"), nullable=False
    )
    temperature_metric = db.Column(db.Float, nullable=False)
    temperature_imperial = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    threshold_reached = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class FloodThreshold(db.Model):
    __tablename__ = "flood_threshold"

    id = db.Column(db.Integer, primary_key=True)
    favorite_city_id = db.Column(
        db.Integer, db.ForeignKey("favorite_city.id"), nullable=False
    )
    precipitation_metric = db.Column(db.Float, nullable=False)
    precipitation_imperial = db.Column(db.Float, nullable=False)
    threshold_reached = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)


class TokenBlocklist(db.Model):
    __tablename__ = "token_blocklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True)
    created_at = db.Column(
        db.DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    expires_at = db.Column(db.DateTime, nullable=False)


class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
