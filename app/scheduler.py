import atexit

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.extensions import db
from app.helpers.generic_helper import create_notification
from app.helpers.weather_helper import WeatherAPI
from app.models.database_model import (
    User,
    StormThreshold,
    HeatwaveThreshold,
    FloodThreshold,
)
from app.controllers.threshold_controller import (
    get_cities_with_thresholds_and_thresholds_raw,
)

scheduler_instance = None
scheduler_started = False


def fetch_weather_data(city_name, is_metric):
    """
    Récupère les données météo pour une ville donnée.
    """
    return WeatherAPI.get_forecast(city_name, 1, "metric" if is_metric else "imperial")


def handle_storm_threshold(city, details, weather_data, user_id, is_metric):
    """
    Gère les seuils de tempête pour une ville donnée.
    """
    storm_threshold = StormThreshold.query.filter_by(
        favorite_city_id=city["city_id"],
        **(
            {
                "wind_speed_metric": details["wind_speed"],
                "gust_speed_metric": details["gust_speed"],
            }
            if is_metric
            else {
                "wind_speed_imperial": details["wind_speed"],
                "gust_speed_imperial": details["gust_speed"],
            }
        ),
    ).first()

    if not storm_threshold:
        return f"No storm threshold found for city {city['city_name']} with details {details}."

    if storm_threshold.threshold_reached:
        return None

    wind_speed = (
        weather_data["current"]["wind_kph"]
        if is_metric
        else weather_data["current"]["wind_mph"]
    )
    gust_speed = (
        weather_data["current"]["gust_kph"]
        if is_metric
        else weather_data["current"]["gust_mph"]
    )
    wind_unit = "km/h" if is_metric else "mph"

    if wind_speed >= details["wind_speed"] and gust_speed >= details["gust_speed"]:
        storm_threshold.threshold_reached = True
        db.session.delete(storm_threshold)
        db.session.commit()
        create_notification(
            user_id=user_id,
            title=f"Storm threshold met for {city['city_name']}",
            message=(
                f"Wind speed threshold: {details['wind_speed']} {wind_unit}, Actual: {wind_speed} {wind_unit}. "
                f"Gust speed threshold: {details['gust_speed']} {wind_unit}, Actual: {gust_speed} {wind_unit}."
            ),
        )
        return f"Storm threshold met for {city['city_name']}."

    return None


def handle_heatwave_threshold(city, details, weather_data, user_id, is_metric):
    """
    Gère les seuils de canicule pour une ville donnée.
    """
    heatwave_threshold = HeatwaveThreshold.query.filter_by(
        favorite_city_id=city["city_id"],
        **(
            {
                "temperature_metric": details["temperature"],
                "humidity": details["humidity"],
            }
            if is_metric
            else {
                "temperature_imperial": details["temperature"],
                "humidity": details["humidity"],
            }
        ),
    ).first()

    if not heatwave_threshold:
        return f"No heatwave threshold found for city {city['city_name']} with details {details}."

    if heatwave_threshold.threshold_reached:
        return None

    temperature = (
        weather_data["current"]["temp_c"]
        if is_metric
        else weather_data["current"]["temp_f"]
    )
    temperature_unit = "°C" if is_metric else "°F"
    humidity = weather_data["current"]["humidity"]

    if temperature >= details["temperature"] and humidity >= details["humidity"]:
        heatwave_threshold.threshold_reached = True
        db.session.delete(heatwave_threshold)
        db.session.commit()
        create_notification(
            user_id=user_id,
            title=f"Heatwave threshold met for {city['city_name']}",
            message=(
                f"Temperature threshold: {details['temperature']} {temperature_unit}, "
                f"Actual: {temperature} {temperature_unit}. "
                f"Humidity threshold: {details['humidity']}%, Actual: {humidity}%."
            ),
        )
        return f"Heatwave threshold met for {city['city_name']}."

    return None


def handle_flood_threshold(city, details, weather_data, user_id, is_metric):
    """
    Gère les seuils d'inondation pour une ville donnée.
    """
    flood_threshold = FloodThreshold.query.filter_by(
        favorite_city_id=city["city_id"],
        **(
            {"precipitation_metric": details["precipitation"]}
            if is_metric
            else {"precipitation_imperial": details["precipitation"]}
        ),
    ).first()

    if not flood_threshold:
        return f"No flood threshold found for city {city['city_name']} with details {details}."

    if flood_threshold.threshold_reached:
        return None

    precipitation = (
        weather_data["current"]["precip_mm"]
        if is_metric
        else weather_data["current"]["precip_in"]
    )
    precipitation_unit = "mm" if is_metric else "in"

    if precipitation >= details["precipitation"]:
        flood_threshold.threshold_reached = True
        db.session.delete(flood_threshold)
        db.session.commit()
        create_notification(
            user_id=user_id,
            title=f"Flood threshold met for {city['city_name']}",
            message=(
                f"Precipitation threshold: {details['precipitation']} {precipitation_unit},"
                f"Actual: {precipitation} {precipitation_unit}."
            ),
        )
        return f"Flood threshold met for {city['city_name']}."

    return None


def get_all_users_and_thresholds():
    """
    Récupérer tous les utilisateurs et leurs seuils associés.
    """
    users = User.query.all()
    result = []

    for user in users:
        try:
            data = get_cities_with_thresholds_and_thresholds_raw(user.id)
            result.append(
                {
                    "user_id": user.id,
                    "preferences": user.preferences.lower(),
                    "data": data,
                }
            )
        except ValueError:
            # Ignore users with no thresholds
            continue

    return result


def compare_weather_and_thresholds(app):
    """
    Tâche principale pour comparer les données météo avec les seuils.
    """
    with app.app_context():
        app.logger.info("Executing compare_weather_and_thresholds task...")

        users_data = get_all_users_and_thresholds()
        if not users_data:
            app.logger.info(
                "No users with thresholds found. Task will wait for next execution."
            )
            return

        for user_data in users_data:
            user_id = user_data["user_id"]
            is_metric = user_data["preferences"] == "metric"
            cities = user_data["data"]

            if not cities:
                app.logger.info(
                    f"No thresholds configured for user ID {user_id}. Skipping this user."
                )
                continue

            for city in cities:
                city_name = city["city_name"]
                thresholds = city["thresholds"]

                app.logger.info(
                    f"Processing city {city_name} for user ID {user_id} with thresholds: {thresholds}"
                )

                if not thresholds:
                    app.logger.info(
                        f"No thresholds found for city {city_name} (user ID: {user_id}). Skipping this city."
                    )
                    continue

                weather_data = fetch_weather_data(city_name, is_metric)

                if "error" in weather_data:
                    app.logger.error(
                        f"Failed to fetch weather data for {city_name}: {weather_data['error']}"
                    )
                    continue

                for threshold in city["thresholds"]:
                    app.logger.info(
                        f"Comparing weather data with threshold: {threshold}"
                    )
                    if threshold["type"] == "storm":
                        message = handle_storm_threshold(
                            city, threshold["details"], weather_data, user_id, is_metric
                        )
                    elif threshold["type"] == "heatwave":
                        message = handle_heatwave_threshold(
                            city, threshold["details"], weather_data, user_id, is_metric
                        )
                    elif threshold["type"] == "flood":
                        message = handle_flood_threshold(
                            city, threshold["details"], weather_data, user_id, is_metric
                        )
                    else:
                        message = f"Unknown threshold type: {threshold['type']}."

                    if message:
                        app.logger.info(message)

        app.logger.info("Completed execution of compare_weather_and_thresholds task.")


def start_scheduler(app):
    """
    Configure et démarre le planificateur APScheduler avec l'application Flask.
    """
    global scheduler_instance, scheduler_started

    if scheduler_started:
        app.logger.info("Scheduler already running. Skipping initialization.")
        return

    scheduler = BackgroundScheduler()
    scheduler.start()

    scheduler.add_job(
        func=lambda: compare_weather_and_thresholds(app),
        trigger=IntervalTrigger(seconds=5),
        id="compare_weather_and_thresholds",
        name="Compare weather data with thresholds every 30 seconds",
        replace_existing=True,
    )

    atexit.register(lambda: scheduler.shutdown())
    scheduler_instance = scheduler
    scheduler_started = True
