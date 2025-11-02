import json
import numpy as np
from core.utils.llm_interface import LLMInterface
from .fetcher import get_weather


def interpret_weathercode(code: int):
    """
    Interpret Open-Meteo WMO weather codes into readable text.
    """
    codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }
    return codes.get(code, "Unknown")


class WeatherAgent:
    def __init__(self):
        self.llm = LLMInterface(model="llama3:8b")
        self.last_city = None
        self.last_coords = None

    def extract_city_and_coords(self, query: str):
        prompt = f"""
        Extract from the question:
        1. City name
        2. Approximate latitude and longitude (decimal degrees)
        
        Respond **only** in this format:
        City: <city>
        Lat: <latitude>
        Lon: <longitude>
        
        Question: "{query}"
        """
        response = self.llm.chat(prompt)
        city, lat, lon = None, None, None
        for line in response.splitlines():
            if line.lower().startswith("city:"):
                city = line.split(":", 1)[1].strip()
                if city.lower() == "none" or city == "":
                    city = None
            elif line.lower().startswith("lat:"):
                try:
                    lat = float(line.split(":", 1)[1].strip())
                except ValueError:
                    lat = None
            elif line.lower().startswith("lon:"):
                try:
                    lon = float(line.split(":", 1)[1].strip())
                except ValueError:
                    lon = None
        return city, lat, lon

    @staticmethod
    def preprocess_weather_data(weather_data: dict):
        """
        Summarize the raw weather JSON into a structured but concise form
        readable by the LLM.
        """
        summary = {}

        # --- Current ---
        current = weather_data.get("current_weather", {})
        summary["current"] = {
            "temperature": current.get("temperature"),
            "windspeed": current.get("windspeed"),
            "direction": current.get("winddirection"),
            "weathercode": current.get("weathercode"),
            "description": interpret_weathercode(current.get("weathercode")),
        }

        # --- Daily forecast ---
        daily = weather_data.get("daily", {})
        times = daily.get("time", [])
        if times:
            for i, date in enumerate(times[:2]):
                tag = "today" if i == 0 else "tomorrow"
                summary[tag] = {
                    "date": date,
                    "t_min": daily.get("temperature_2m_min", [None])[i],
                    "t_max": daily.get("temperature_2m_max", [None])[i],
                    "precip_mm": daily.get("precipitation_sum", [None])[i],
                    "precip_prob": daily.get("precipitation_probability_max", [None])[i],
                    "sunshine_hours": round(
                        (daily.get("sunshine_duration", [0])[i] or 0) / 3600, 1
                    ),
                    "weathercode": daily.get("weathercode", [None])[i],
                    "description": interpret_weathercode(
                        daily.get("weathercode", [None])[i]
                    ),
                }

        # --- Hourly summary (next 24h) ---
        hourly = weather_data.get("hourly", {})
        if "temperature_2m" in hourly:
            temps = np.array(hourly.get("temperature_2m", [])[:24])
            clouds = np.array(hourly.get("cloud_cover", [])[:24])
            probs = np.array(hourly.get("precipitation_probability", [])[:24])
            summary["next_24h"] = {
                "avg_temp": float(np.nanmean(temps)) if len(temps) else None,
                "avg_clouds": float(np.nanmean(clouds)) if len(clouds) else None,
                "max_precip_prob": float(np.nanmax(probs)) if len(probs) else None,
            }

        return summary

    def summarize_weather(self, city: str, query: str, weather_data: dict):
        if not weather_data:
            return "Sorry, I couldn't retrieve the weather data."

        summary = self.preprocess_weather_data(weather_data)
        compact_json = json.dumps(summary, indent=2)

        prompt = f"""
        You are NEXCAI, an advanced and precise weather analyst.

        The user asked: "{query}"
        City: {city}
        Here's the structured weather data:
        {compact_json}

        Instructions:
        - Understand weather codes: 0=clear,1=mainly clear,2=partly cloudy,3=overcast,
          45–48=fog,51–67=drizzle/rain,71–77=snow,80–82=showers,95–99=thunderstorm.
        - precipitation_sum < 1 → "mostly dry", 1–5 → "light rain", 5–20 → "moderate rain", >20 → "heavy rain".
        - sunshine_hours > 5 → "mostly sunny".
        - precipitation_prob > 70 → "high chance of rain".
        - Answer for only the requested day. If today is asked give today, if tomorrow is asked, give tomorrow only.
        - If the question is specific (like 'will it rain tomorrow?'), answer directly yes/no and short explanation.
        - If general (like 'how will it be tomorrow?'), summarize temperature, cloudiness, and rain probability in 1 paragraph.
        - Be factual, concise, 3 4 sentences max and sound like an energetic weather reporter.
        """

        return self.llm.chat(prompt)

    def run(self, query: str):
        city, lat, lon = self.extract_city_and_coords(query)
        if not city or not lat or not lon:
            if self.last_city and self.last_coords:
                city, (lat, lon) = self.last_city, self.last_coords
            else:
                return "Please specify a city first."
        else:
            self.last_city = city
            self.last_coords = (lat, lon)

        weather_data = get_weather(lat, lon)
        return self.summarize_weather(city, query, weather_data)
