from flask import jsonify, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.user import (
    FavoriteCity,
    StormThreshold,
    HeatwaveThreshold,
    FloodThreshold,
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
              description: ID de la ville favorite.
              example: 1
            wind_speed:
              type: float
              description: Vitesse minimale du vent (en km/h).
              example: 70.0
            gust_speed:
              type: float
              description: Vitesse minimale des rafales (en km/h).
              example: 100.0
    responses:
      201:
        description: Seuil de tempête ajouté avec succès.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Tempête threshold created successfully"
      400:
        description: Données manquantes ou invalides.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Missing required fields"
      404:
        description: Ville favorite introuvable.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Favorite city not found"
      500:
        description: Erreur serveur inattendue.
        schema:
          type: object
          properties:
            error:
              type: string
              example: "Unexpected error: ..."
    """
    try:
        data = request.json
        favorite_city_id = data.get("favorite_city_id")
        wind_speed = data.get("wind_speed")
        gust_speed = data.get("gust_speed")

        if not favorite_city_id or not wind_speed or not gust_speed:
            return jsonify({"error": "Missing required fields"}), 400

        favorite_city = FavoriteCity.query.get(favorite_city_id)
        if not favorite_city:
            return jsonify({"error": "Favorite city not found"}), 404

        threshold = StormThreshold(
            favorite_city_id=favorite_city_id,
            wind_speed=wind_speed,
            gust_speed=gust_speed,
        )
        db.session.add(threshold)
        db.session.commit()

        return jsonify({"message": "Tempête threshold created successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


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
                      description: ID de la ville favorite.
                      example: 1
                  precipitation:
                      type: float
                      description: Précipitation minimale (en mm).
                      example: 50.0
    responses:
      201:
        description: Seuil d'inondation ajouté avec succès.
        schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Inondation threshold created successfully"
      400:
        description: Données manquantes ou invalides.
        schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Missing required fields"
      404:
        description: Ville favorite introuvable.
        schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Favorite city not found"
      500:
        description: Erreur serveur inattendue.
        schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Unexpected error: ..."
    """
    try:
        data = request.json
        favorite_city_id = data.get("favorite_city_id")
        precipitation = data.get("precipitation")

        if not favorite_city_id or not precipitation:
            return jsonify({"error": "Missing required fields"}), 400

        favorite_city = FavoriteCity.query.get(favorite_city_id)
        if not favorite_city:
            return jsonify({"error": "Favorite city not found"}), 404

        threshold = FloodThreshold(
            favorite_city_id=favorite_city_id, precipitation=precipitation
        )
        db.session.add(threshold)
        db.session.commit()

        return jsonify({"message": "Inondation threshold created successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


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
                  description: ID de la ville favorite.
                  example: 1
              temperature:
                  type: float
                  description: Température minimale (en °C).
                  example: 40.0
              humidity:
                  type: float
                  description: Humidité minimale (en %).
                  example: 80.0
    responses:
      201:
        description: Seuil de canicule ajouté avec succès.
        schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Canicule threshold created successfully"
      400:
        description: Données manquantes ou invalides.
        schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Missing required fields"
      404:
        description: Ville favorite introuvable.
        schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Favorite city not found"
      500:
        description: Erreur serveur inattendue.
        schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Unexpected error: ..."
    """
    try:
        data = request.json
        favorite_city_id = data.get("favorite_city_id")
        temperature = data.get("temperature")
        humidity = data.get("humidity")

        if not favorite_city_id or not temperature or not humidity:
            return jsonify({"error": "Missing required fields"}), 400

        favorite_city = FavoriteCity.query.get(favorite_city_id)
        if not favorite_city:
            return jsonify({"error": "Favorite city not found"}), 404

        threshold = HeatwaveThreshold(
            favorite_city_id=favorite_city_id,
            temperature=temperature,
            humidity=humidity,
        )
        db.session.add(threshold)
        db.session.commit()

        return jsonify({"message": "Canicule threshold created successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


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
            threshold_id:
              type: integer
              description: ID du seuil.
              example: 1
            threshold_type:
              type: string
              description: Type de seuil ("storm", "heatwave", "flood").
              example: "storm"
    responses:
      200:
        description: Seuil supprimé avec succès.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Threshold deleted successfully"
      400:
        description: Données manquantes ou invalides.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Missing required fields"
      404:
        description: Seuil introuvable.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Threshold not found"
      500:
        description: Erreur serveur inattendue.
        schema:
          type: object
          properties:
            message:
              type: string
              example: "Unexpected error: ..."
    """
    try:
        data = request.json
        threshold_id = data.get("threshold_id")
        threshold_type = data.get("threshold_type")

        if not threshold_id or not threshold_type:
            return jsonify({"error": "Missing required fields"}), 400

        if threshold_type == "storm":
            threshold = StormThreshold.query.get(threshold_id)
        elif threshold_type == "heatwave":
            threshold = HeatwaveThreshold.query.get(threshold_id)
        elif threshold_type == "flood":
            threshold = FloodThreshold.query.get(threshold_id)
        else:
            return jsonify({"error": "Invalid threshold type"}), 400

        if not threshold:
            return jsonify({"error": "Threshold not found"}), 404

        db.session.delete(threshold)
        db.session.commit()
        return jsonify({"message": "Threshold deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


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
      - name: favorite_city_id
        in: query
        required: true
        description: ID de la ville favorite.
        schema:
          type: integer
    responses:
      200:
        description: Liste des seuils récupérée avec succès.
        schema:
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
      404:
        description: Ville favorite introuvable.
        schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Favorite city not found"
      500:
        description: Erreur serveur inattendue.
        schema:
              type: object
              properties:
                error:
                  type: string
                  example: "Unexpected error: ..."
    """
    try:
        favorite_city_id = request.args.get("favorite_city_id", type=int)
        if not favorite_city_id:
            return jsonify({"error": "favorite_city_id is required"}), 400

        favorite_city = FavoriteCity.query.get(favorite_city_id)
        if not favorite_city:
            return jsonify({"error": "Favorite city not found"}), 404

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
        return jsonify(thresholds), 200
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500
