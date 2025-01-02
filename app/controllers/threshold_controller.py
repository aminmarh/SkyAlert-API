from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.extensions import db
from app.helpers.generic_helper import convert_units
from app.models.user import (
    User,
    FavoriteCity,
    StormThreshold,
    HeatwaveThreshold,
    FloodThreshold,
)
from app.schemas.threshold_schema import (
    StormSchema,
    HeatwaveSchema,
    FloodSchema,
    GetThresholdSchema,
    DeleteThresholdSchema,
)


@jwt_required()
def create_storm_threshold():
    """
    Ajouter un seuil pour la tempête.
    ---
    tags:
      - Thresholds
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            favorite_city_id:
              type: integer
              description: ID of the favorite city
              example: 1
            wind_speed:
              type: float
              description: Minimum wind speed
              example: 70.0
            gust_speed:
              type: float
              description: Minimum gust speed
              example: 100.0
    responses:
      201:
        description: Storm threshold created successfully
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                favorite_city_id:
                  type: integer
                  example: 1
                wind_speed_metric:
                  type: float
                  example: 70.0
                gust_speed_metric:
                  type: float
                  example: 100.0
                wind_speed_imperial:
                  type: float
                  example: 43.496
                gust_speed_imperial:
                  type: float
                  example: 62.1371
            message:
              type: string
              example: Storm threshold created successfully
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
              example: {"wind_speed": ["Not a valid number"]}
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
              example: Favorite city not found
    """
    user = User.query.get(get_jwt_identity())
    data = request.json

    try:
        validated_data = StormSchema().load(data)
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
    favorite_city_id = validated_data["favorite_city_id"]
    wind_speed = validated_data["wind_speed"]
    gust_speed = validated_data["gust_speed"]

    favorite_city = FavoriteCity.query.get(favorite_city_id)
    if not favorite_city:
        return (
            jsonify(
                {"status": "error", "data": None, "message": "Favorite city not found"}
            ),
            404,
        )

    user_units = user.preferences

    existing_threshold = StormThreshold.query.filter(
        StormThreshold.favorite_city_id == favorite_city_id,
        StormThreshold.wind_speed_metric == wind_speed,
        StormThreshold.gust_speed_metric == gust_speed,
    ).first()

    if existing_threshold:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "A storm threshold with the same values already exists for this city",
                }
            ),
            400,
        )

    if user_units == "metric":
        wind_speed_imperial = convert_units(
            wind_speed, "metric", "imperial", "wind_speed"
        )
        gust_speed_imperial = convert_units(
            gust_speed, "metric", "imperial", "wind_speed"
        )
        wind_speed_metric = wind_speed
        gust_speed_metric = gust_speed
    else:
        wind_speed_metric = convert_units(
            wind_speed, "imperial", "metric", "wind_speed"
        )
        gust_speed_metric = convert_units(
            gust_speed, "imperial", "metric", "wind_speed"
        )
        wind_speed_imperial = wind_speed
        gust_speed_imperial = gust_speed

    threshold = StormThreshold(
        favorite_city_id=favorite_city_id,
        wind_speed_metric=wind_speed_metric,
        wind_speed_imperial=wind_speed_imperial,
        gust_speed_metric=gust_speed_metric,
        gust_speed_imperial=gust_speed_imperial,
    )
    db.session.add(threshold)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "favorite_city_id": favorite_city_id,
                    "wind_speed_metric": wind_speed_metric,
                    "gust_speed_metric": gust_speed_metric,
                    "wind_speed_imperial": wind_speed_imperial,
                    "gust_speed_imperial": gust_speed_imperial,
                },
                "message": "Storm threshold created successfully",
            }
        ),
        201,
    )


@jwt_required()
def create_flood_threshold():
    """
    Ajouter un seuil pour l'inondation.
    ---
    tags:
      - Thresholds
    security:
      - Bearer: []
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              favorite_city_id:
                type: integer
                description: ID the favorite city
                example: 1
              precipitation:
                type: float
                description: Minimum precipitation
                example: 50.0
    responses:
      201:
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                favorite_city_id:
                  type: integer
                  example: 1
                precipitation_metric:
                  type: float
                  example: 50.0
                precipitation_imperial:
                  type: float
                  example: 1.9685
            message:
              type: string
              example: Flood threshold created successfully
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
              example: {"precipitation": ["Not a valid number"]}
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
              example: Favorite city not found
    """
    user = User.query.get(get_jwt_identity())
    data = request.json

    try:
        validated_data = FloodSchema().load(data)
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

    favorite_city_id = validated_data["favorite_city_id"]
    precipitation = validated_data["precipitation"]

    favorite_city = FavoriteCity.query.get(favorite_city_id)
    if not favorite_city:
        return (
            jsonify(
                {"status": "error", "data": None, "message": "Favorite city not found"}
            ),
            404,
        )

    user_units = user.preferences

    existing_threshold = FloodThreshold.query.filter(
        FloodThreshold.favorite_city_id == favorite_city_id,
        (
            (FloodThreshold.precipitation_metric == precipitation)
            if user_units == "metric"
            else (FloodThreshold.precipitation_imperial == precipitation)
        ),
    ).first()

    if existing_threshold:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "A flood threshold with the same values already exists for this city",
                }
            ),
            400,
        )

    if user_units == "metric":
        precipitation_imperial = convert_units(
            precipitation, "metric", "imperial", "precipitation"
        )
        precipitation_metric = precipitation
    else:
        precipitation_metric = convert_units(
            precipitation, "imperial", "metric", "precipitation"
        )
        precipitation_imperial = precipitation

    threshold = FloodThreshold(
        favorite_city_id=favorite_city_id,
        precipitation_metric=precipitation_metric,
        precipitation_imperial=precipitation_imperial,
    )
    db.session.add(threshold)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "favorite_city_id": favorite_city_id,
                    "precipitation_metric": precipitation_metric,
                    "precipitation_imperial": precipitation_imperial,
                },
                "message": "Flood threshold created successfully",
            }
        ),
        201,
    )


@jwt_required()
def create_heatwave_threshold():
    """
    Ajouter un seuil pour la canicule.
    ---
    tags:
      - Thresholds
    security:
      - Bearer: []
    parameters:
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              favorite_city_id:
                type: integer
                description: ID the favorite city
                example: 1
              temperature:
                type: float
                description: Minimum temperature
                example: 40.0
              humidity:
                type: float
                description: Minimum humidity
                example: 80.0
    responses:
      201:
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            data:
              type: object
              properties:
                favorite_city_id:
                  type: integer
                  example: 1
                temperature_metric:
                  type: float
                  example: 35.0
                temperature_imperial:
                  type: float
                  example: 95.0
                humidity:
                  type: float
                  example: 80.0
            message:
              type: string
              example: HeatWave threshold created successfully
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
              example: {"temperature": ["Not a valid number"]}
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
              example: Favorite city not found
    """
    user = User.query.get(get_jwt_identity())
    data = request.json

    try:
        validated_data = HeatwaveSchema().load(data)
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

    favorite_city_id = validated_data["favorite_city_id"]
    temperature = validated_data["temperature"]
    humidity = validated_data["humidity"]

    favorite_city = FavoriteCity.query.get(favorite_city_id)
    if not favorite_city:
        return (
            jsonify(
                {"status": "error", "data": None, "message": "Favorite city not found"}
            ),
            404,
        )

    user_units = user.preferences

    existing_threshold = HeatwaveThreshold.query.filter(
        HeatwaveThreshold.favorite_city_id == favorite_city_id,
        HeatwaveThreshold.temperature_metric == temperature,
        HeatwaveThreshold.humidity == humidity,
    ).first()

    if existing_threshold:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "A heatwave threshold with the same values already exists for this city",
                }
            ),
            400,
        )

    if user_units == "metric":
        temperature_imperial = convert_units(
            temperature, "metric", "imperial", "temperature"
        )
        temperature_metric = temperature
    else:
        temperature_metric = convert_units(
            temperature, "imperial", "metric", "temperature"
        )
        temperature_imperial = temperature

    threshold = HeatwaveThreshold(
        favorite_city_id=favorite_city_id,
        temperature_metric=temperature_metric,
        temperature_imperial=temperature_imperial,
        humidity=humidity,
    )
    db.session.add(threshold)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "favorite_city_id": favorite_city_id,
                    "temperature_metric": temperature_metric,
                    "temperature_imperial": temperature_imperial,
                    "humidity": humidity,
                },
                "message": "HeatWave threshold created successfully",
            }
        ),
        201,
    )


@jwt_required()
def delete_threshold():
    """
    Supprimer un seuil.
    ---
    tags:
      - Thresholds
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            favorite_city_id:
              type: integer
              description: ID the favorite city
              example: 1
            threshold_id:
              type: integer
              description: ID the threshold
              example: 1
            threshold_type:
              type: string
              description: Type of the threshold
              example: "storm"
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
                favorite_city_id:
                  type: integer
                  example: 1
                threshold_id:
                  type: integer
                  example: 2
                threshold_type:
                  type: srting
                  example: "storm"
            message:
              type: string
              example: Threshold deleted successfully
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
              example: "Validation failed"
            errors:
              type: object
              example: {"threshold_type": ["Invalid Threshold Type"]}
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
              example: "Threshold not found"
    """
    data = request.json
    try:
        validated_data = DeleteThresholdSchema().load(data)
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

    favorite_city_id = validated_data["favorite_city_id"]
    threshold_id = validated_data["threshold_id"]
    threshold_type = validated_data["threshold_type"]

    favorite_city = FavoriteCity.query.get(favorite_city_id)
    if not favorite_city:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Favorite city not found",
                }
            ),
            404,
        )

    if threshold_type == "storm":
        threshold = StormThreshold.query.filter_by(
            id=threshold_id, favorite_city_id=favorite_city_id
        ).first()
    elif threshold_type == "heatwave":
        threshold = HeatwaveThreshold.query.filter_by(
            id=threshold_id, favorite_city_id=favorite_city_id
        ).first()
    elif threshold_type == "flood":
        threshold = FloodThreshold.query.filter_by(
            id=threshold_id, favorite_city_id=favorite_city_id
        ).first()
    else:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Invalid threshold type",
                }
            ),
            400,
        )

    if not threshold:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Threshold not found",
                }
            ),
            404,
        )

    db.session.delete(threshold)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "favorite_city_id": favorite_city_id,
                    "threshold_id": threshold_id,
                    "threshold_type": threshold_type,
                },
                "message": "Threshold deleted successfully",
            }
        ),
        200,
    )


@jwt_required()
def get_thresholds():
    """
    Récupérer les seuils d'une ville favorite.
    ---
    tags:
      - Thresholds
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            favorite_city_id:
              type: integer
              description: ID the favorite city
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
                storm:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      wind_speed:
                        type: float
                      gust_speed:
                        type: float
                      created_at:
                        type: string
                        format: date-time
                heatwave:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      temperature:
                        type: float
                      humidity:
                        type: float
                      created_at:
                        type: string
                        format: date-time
                flood:
                  type: array
                  items:
                    type: object
                    properties:
                      id:
                        type: integer
                      precipitation:
                        type: float
                      created_at:
                        type: string
                        format: date-time
            message:
              type: string
              example: Thresholds retrieved successfully
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
              example: "Validation failed"
            errors:
              type: object
              example: {"favorite_city_id": ["Not a valid number"]}
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
              example: "Favorite city not found"
    """
    user = User.query.get(get_jwt_identity())
    data = request.json

    try:
        validated_data = GetThresholdSchema().load(data)
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

    favorite_city_id = validated_data["favorite_city_id"]

    favorite_city = FavoriteCity.query.get(favorite_city_id)
    if not favorite_city:
        return (
            jsonify(
                {
                    "status": "error",
                    "data": None,
                    "message": "Favorite city not found",
                }
            ),
            404,
        )

    user_units = user.preferences

    thresholds = {
        "storm": [
            {
                "id": t.id,
                "wind_speed": (
                    t.wind_speed_imperial
                    if user_units == "imperial"
                    else t.wind_speed_metric
                ),
                "gust_speed": (
                    t.gust_speed_imperial
                    if user_units == "imperial"
                    else t.gust_speed_metric
                ),
                "created_at": t.created_at.isoformat(),
            }
            for t in favorite_city.storm_thresholds
        ],
        "heatwave": [
            {
                "id": t.id,
                "temperature": (
                    t.temperature_imperial
                    if user_units == "imperial"
                    else t.temperature_metric
                ),
                "humidity": t.humidity,
                "created_at": t.created_at.isoformat(),
            }
            for t in favorite_city.heatwave_thresholds
        ],
        "flood": [
            {
                "id": t.id,
                "precipitation": (
                    t.precipitation_imperial
                    if user_units == "imperial"
                    else t.precipitation_metric
                ),
                "created_at": t.created_at.isoformat(),
            }
            for t in favorite_city.flood_thresholds
        ],
    }
    return (
        jsonify(
            {
                "status": "success",
                "data": thresholds,
                "message": "Thresholds retrieved successfully",
            }
        ),
        200,
    )


@jwt_required()
def get_cities_with_thresholds():
    """
    Récupérer les villes ayant au moins un seuil.
    ---
    tags:
      - Thresholds
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
                  city_id:
                    type: integer
                    example: 1
                  city_name:
                    type: string
                    example: "Paris"
            message:
              type: string
              example: "Cities with thresholds retrieved successfully"
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

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

    cities_with_thresholds = (
        db.session.query(FavoriteCity)
        .filter(
            FavoriteCity.user_id == user_id,
            db.or_(
                FavoriteCity.storm_thresholds.any(),
                FavoriteCity.heatwave_thresholds.any(),
                FavoriteCity.flood_thresholds.any(),
            ),
        )
        .all()
    )

    result = [
        {"city_id": city.id, "city_name": city.city} for city in cities_with_thresholds
    ]

    return (
        jsonify(
            {
                "status": "success",
                "data": result,
                "message": "Cities with thresholds retrieved successfully",
            }
        ),
        200,
    )
