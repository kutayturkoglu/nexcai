import requests

def get_weather(lat: float, lon: float, forecast_days: int = 16):
    """
    Fetch detailed multi-day weather data from Open-Meteo (max info).
    Returns current, hourly, and daily data for up to 16 days.
    """

    url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&current_weather=true"
        "&hourly=temperature_2m,apparent_temperature,precipitation,precipitation_probability,"
        "cloud_cover,cloud_cover_low,cloud_cover_mid,cloud_cover_high,weathercode,"
        "windspeed_10m,winddirection_10m,visibility"
        "&daily=temperature_2m_max,temperature_2m_min,apparent_temperature_max,apparent_temperature_min,"
        "precipitation_sum,precipitation_hours,precipitation_probability_max,sunshine_duration,"
        "uv_index_max,weathercode,wind_speed_10m_max,wind_gusts_10m_max,sunrise,sunset"
        f"&forecast_days={forecast_days}"
        "&timezone=auto"
    )

    try:
        r = requests.get(url)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Weather API error:", e)
        return {}
