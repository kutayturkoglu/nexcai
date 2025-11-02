import requests

def get_weather(lat: float, lon: float):
    """
        Fetch current weather data from Open-Meteo
    """

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}&current_weather=true" 
    )
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        return data.get("current_weather", {})
    except Exception as e:
        print(f"Weather API error {e}")
        return {}
    