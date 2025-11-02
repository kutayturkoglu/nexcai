from core.utils.llm_interface import LLMInterface
from .fetcher import get_weather
class WeatherAgent:
    """
        Weather agent that uses the LLM to:
        1. Extract the city name + coordinates.
        2. Fetch raw Open-Meteo data.
        3. Summarizes it RAG.
    """

    def __init__(self):
        self.llm = LLMInterface(model="llama3:8b")

    def extract_city_and_coords(self, query: str):
        """
            Ask the LLM to return both the ciy and its coordinates
        """
        prompt = f"""
            From the following user question, extract:
            1. The city name.
            2. Its approximate latitude and longitude (decimal degrees).

            Respond ONLY in this format:
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
            elif line.lower().startswith("lat:"):
                lat = float(line.split(":", 1)[1].strip())
            elif line.lower().startswith("lon:"):
                lon = float(line.split(":", 1)[1].strip())
        return city, lat, lon
    
    def summarize_weather(self, city: str, query: str, weather_data: dict):
        """
            Let the LLM as a summarizer over the raw weather data
        """
        if not weather_data:
            return "Sorry, I couldn't retrieve the weather data"
        
        prompt = f"""
            You are Nexcai, an intelligent assistant.

            The user asked: "{query}"
            The weather data for {city} is below (JSON):
            {weather_data}

            Summarize this information naturally in English
            just like a weather forecast reporter would while resonding
            to the question within the given data. Energetic
            and pleasant.
            """
        return self.llm.chat(prompt)
    
    def run(self, query: str):
        city, lat, lon = self.extract_city_and_coords(query)
        if not city or not lat or not lon:
            return "I couldn't extract a valid city and coordinates."
        weather_data = get_weather(lat, lon)
        return self.summarize_weather(city, query, weather_data)