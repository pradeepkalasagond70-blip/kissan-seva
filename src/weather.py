import requests


# --------------------------------------------------
# Open-Meteo API URLs
# --------------------------------------------------

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


# --------------------------------------------------
# Geocode Location
# --------------------------------------------------

def geocode_location(location):

    params = {
        "name": location,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(
        GEOCODING_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        raise ValueError(
            f"Location not found: {location}"
        )

    result = data["results"][0]

    return {
        "name": result["name"],
        "country": result.get("country"),
        "latitude": result["latitude"],
        "longitude": result["longitude"]
    }


# --------------------------------------------------
# Get Weather
# --------------------------------------------------

def get_weather(latitude, longitude):

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "rain",
            "wind_speed_10m"
        ]),

        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "precipitation_sum",
            "et0_fao_evapotranspiration"
        ]),

        "forecast_days": 7,

        "timezone": "auto"
    }

    response = requests.get(
        WEATHER_URL,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    return response.json()


# --------------------------------------------------
# Get Weather By Location
# --------------------------------------------------

def get_weather_by_location(location):

    location_data = geocode_location(location)

    weather_data = get_weather(
        location_data["latitude"],
        location_data["longitude"]
    )

    return {
        "location": location_data,
        "weather": weather_data
    }