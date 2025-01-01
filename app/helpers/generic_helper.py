def convert_units(value, from_unit, to_unit, unit_type):
    """
    Convert a value between imperial and metric units for wind speed, temperature, or precipitation.

    :param value: float, value to convert
    :param from_unit: str, source unit ('metric' or 'imperial')
    :param to_unit: str, target unit ('metric' or 'imperial')
    :param unit_type: str, type of unit ('wind_speed', 'temperature', 'precipitation')
    :return: int, converted value as an integer
    """
    if from_unit == to_unit:
        return int(round(value))  # No conversion needed, round and ensure integer

    if unit_type == "wind_speed":  # Convert km/h <-> miles/h
        if from_unit == "metric" and to_unit == "imperial":
            return int(round(value * 0.621371))
        elif from_unit == "imperial" and to_unit == "metric":
            return int(round(value / 0.621371))

    elif unit_type == "temperature":  # Convert Celsius <-> Fahrenheit
        if from_unit == "metric" and to_unit == "imperial":
            return int(round((value * 9 / 5) + 32))
        elif from_unit == "imperial" and to_unit == "metric":
            return int(round((value - 32) * 5 / 9))

    elif unit_type == "precipitation":  # Convert mm <-> inches
        if from_unit == "metric" and to_unit == "imperial":
            return int(round(value * 0.0393701))
        elif from_unit == "imperial" and to_unit == "metric":
            return int(round(value / 0.0393701))

    raise ValueError(
        f"Unsupported conversion from {from_unit} to {to_unit} for {unit_type}"
    )
