from flask import jsonify, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.extensions import db
from app.models.user import (
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
                wind_speed:
                  type: float
                  example: 70.0
                gust_speed:
                  type: float
                  example: 100.0
            message:
              type: string
              example: Storm threshold created successfully
      400:
        description: Validation failed
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
        description: Favorite city not found
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

    threshold = StormThreshold(
        favorite_city_id=favorite_city_id,
        wind_speed=wind_speed,
        gust_speed=gust_speed,
    )
    db.session.add(threshold)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "favorite_city_id": favorite_city_id,
                    "wind_speed": wind_speed,
                    "gust_speed": gust_speed,
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
                precipitation:
                  type: float
                  example: 50.0
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

    threshold = FloodThreshold(
        favorite_city_id=favorite_city_id, precipitation=precipitation
    )
    db.session.add(threshold)
    db.session.commit()

    return (
        jsonify(
            {
                "status": "success",
                "data": {
                    "favorite_city_id": favorite_city_id,
                    "precipitation": precipitation,
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
                temperature:
                  type: float
                  example: 35.0
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

    threshold = HeatwaveThreshold(
        favorite_city_id=favorite_city_id,
        temperature=temperature,
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
                    "temperature": temperature,
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

    thresholds = {
        "storm": [
            {
                "id": t.id,
                "wind_speed": t.wind_speed,
                "gust_speed": t.gust_speed,
                "created_at": t.created_at.isoformat(),
            }
            for t in favorite_city.storm_thresholds
        ],
        "heatwave": [
            {
                "id": t.id,
                "temperature": t.temperature,
                "humidity": t.humidity,
                "created_at": t.created_at.isoformat(),
            }
            for t in favorite_city.heatwave_thresholds
        ],
        "flood": [
            {
                "id": t.id,
                "precipitation": t.precipitation,
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
