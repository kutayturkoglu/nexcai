import json
from core.utils.llm_interface import LLMInterface

def route_query(user_message: str) -> str:
    """
    Sends the user's message to the LLM for intent classification.
    Returns one of: "weather" or "general".
    """

    prompt = f"""
        You are a precise intent classifier for a modular AI assistant called NEXCAI.

        Your job is to analyze the user's message and decide which type of agent should handle it.

        Available intents:
        - weather: when the user asks about weather, temperature, rain, wind, sun, or forecasts.
        - general: for normal conversation, greetings, or anything else that doesn't fit.

        Respond **only** in pure JSON format:
        {{"intent": "weather"}}

        User message: "{user_message}"
    """

    llm = LLMInterface(model="llama3:8b")
    response = llm.chat(prompt)

    try:
        data = json.loads(response)
        intent = data.get("intent", "general").lower()
        if intent not in ["weather", "general"]:
            intent = "general"
    except Exception:
        intent = "general"

    return intent