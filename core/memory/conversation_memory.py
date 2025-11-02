from typing import List, Dict

class ConversationMemory:
    """
        Keeps track of the last few chat turns between user and assistant.
        This allows Jarvis to maintain short-term context.
    """

    def __init__(self, max_length: int=10):
        # stores messages as [{"role": "user"/"assistant", "content": "..."}]
        self.history: List[Dict[str, str]] = []
        self.max_length = max_length
    def add(self, role:str, content:str):
        """
            Add a new message to memory.
        """
        self.history.append({"role": role, "content": content})
        if len(self.history) > self.max_length:
            self.history.pop(0)
        
    def get_context(self) -> str:
        """
            Return concatenated conversation history as text context.
        """
        context_lines = [f"{m['role'].capitalize()}: {m['content']}" for m in self.history]
        return "\n".join(context_lines)

    def clear(self):
        """Clear the conversation memory."""
        self.history = []