import json
from core.utils.llm_interface import LLMInterface

def route_query(user_message: str) -> str:
    """
    Sends the user's message to the LLM for intent classification.
    Returns one of: "weather", "calendar", or "general".
    """

    prompt = f"""
    You are a precise intent classifier for a modular AI assistant called NEXCAI.

    Your job is to analyze the user's message and decide which type of agent should handle it.

    Available intents:
    - weather → for any question about temperature, rain, wind, sun, or forecasts.
    - calendar → for anything related to scheduling, time, or events (e.g. “create a meeting”, “what’s on my schedule”).
    - general → for normal conversation, greetings, or unrelated questions.

    Respond only in pure JSON format like:
    {{"intent": "weather"}}

    User message: "{user_message}"
    """

    llm = LLMInterface(model="llama3:8b")
    response = llm.chat(prompt)

    try:
        data = json.loads(response)
        intent = data.get("intent", "general").lower()
        if intent not in ["weather", "calendar", "general"]:
            intent = "general"
    except Exception:
        intent = "general"

    return intent
