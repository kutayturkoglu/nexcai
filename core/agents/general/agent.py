from core.utils.llm_interface import LLMInterface

class GeneralAgent:
    """
        Handles general conversations or questions.
    """

    def __init__(self):
        self.llm = LLMInterface(model="llama3:8b")
    
    def run(self, query: str):
        prompt = f"""
            You are NEXCAI, a helpful, polite assistant. Respond 
            naturally in English for the following user input: 
            "{query}"
            """
        return self.llm.chat(prompt)