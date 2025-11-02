from core.utils.llm_interface import LLMInterface
from core.memory.conversation_memory import ConversationMemory

class GeneralAgent:
    """
        Handles general conversations or questions.
    """

    def __init__(self):
        self.llm = LLMInterface(model="llama3:8b")
        self.memory = ConversationMemory(max_length=10)
    
    def run(self, query: str):
        self.memory.add("user", query)
        context = self.memory.get_context()
        prompt = f"""
            You are NEXCAI, a helpful, polite assistant.
            Respond naturally in English using the context below.

            Conversation so far:
            {context}

            Assistant:
        """
        response = self.llm.chat(prompt)
        self.memory.add("assistant", response)
        return response