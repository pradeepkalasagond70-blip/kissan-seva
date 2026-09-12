def get_irrigation_recommendation(weather_data):
    """
    Generate an explainable irrigation recommendation
    using tomorrow's weather forecast.
    """

    daily = weather_data.get("daily", {})

    if not daily:
        return {
            "status": "error",
            "recommendation": "UNAVAILABLE",
            "reason": "Weather forecast data is unavailable."
        }

    # --------------------------------------------------
    # Tomorrow's Forecast
    # --------------------------------------------------

    rain_probability = daily.get(
        "precipitation_probability_max", [None]
    )[1]

    rainfall = daily.get(
        "precipitation_sum", [None]
    )[1]

    et0 = daily.get(
        "et0_fao_evapotranspiration", [None]
    )[1]

    temperature_max = daily.get(
        "temperature_2m_max", [None]
    )[1]

    # --------------------------------------------------
    # Validate Required Data
    # --------------------------------------------------

    if (
        rain_probability is None
        or rainfall is None
        or et0 is None
    ):
        return {
            "status": "error",
            "recommendation": "UNAVAILABLE",
            "reason": "Required weather information is missing."
        }

    # --------------------------------------------------
    # Irrigation Decision Logic
    # --------------------------------------------------

    # Case 1: Strong rainfall expected
    if rain_probability >= 60 and rainfall >= 5:

        recommendation = "IRRIGATION NOT REQUIRED"

        reason = (
            f"Rain is likely tomorrow "
            f"({rain_probability}% probability, "
            f"{rainfall:.1f} mm expected). "
            "Natural rainfall may provide sufficient water."
        )

    # Case 2: Moderate rainfall expected
    elif rain_probability >= 40 and rainfall >= 2:

        recommendation = "IRRIGATION MAY BE REQUIRED"

        reason = (
            f"Moderate rainfall is possible tomorrow "
            f"({rain_probability}% probability, "
            f"{rainfall:.1f} mm expected). "
            "Consider delaying irrigation and reassessing rainfall."
        )

    # Case 3: Low rainfall + high water demand
    elif rainfall < 2 and et0 >= 4:

        recommendation = "IRRIGATION REQUIRED"

        reason = (
            f"Low rainfall is expected ({rainfall:.1f} mm) "
            f"while estimated crop water loss is relatively high "
            f"(ET₀ {et0:.1f} mm)."
        )

    # Case 4: Uncertain conditions
    else:

        recommendation = "IRRIGATION MAY BE REQUIRED"

        reason = (
            f"Only {rainfall:.1f} mm rainfall is expected tomorrow "
            f"with ET₀ of {et0:.1f} mm. "
            "Check soil moisture before irrigating."
        )

    # --------------------------------------------------
    # Return Result
    # --------------------------------------------------

    return {
        "status": "success",
        "recommendation": recommendation,
        "reason": reason,
        "rain_probability": rain_probability,
        "expected_rainfall_mm": rainfall,
        "et0_mm": et0,
        "temperature_max_c": temperature_max
    }