from core.utils.llm_interface import LLMInterface
from core.memory.conversation_memory import ConversationMemory
from core.memory.longterm_memory import LongTermMemory


class GeneralAgent:
    """
    General-purpose conversational agent for NEXCAI.
    Combines:
    - short-term chat memory (recent conversation context)
    - long-term semantic memory (FAISS-based user facts)
    """

    def __init__(self):
        # Initialize LLM and both memory systems
        self.llm = LLMInterface(model="llama3:8b")
        self.memory = ConversationMemory(max_length=10)
        self.longterm_memory = LongTermMemory()

    def run(self, query: str):
        """
        Run the General Agent:
        1. Add user's message to short-term memory
        2. Retrieve relevant long-term memories
        3. Send combined context to LLM
        4. Add assistant's reply to memory
        5. Teach LTM (if LLM deems it valuable)
        """

        # ---- Add to short-term memory ---
        self.memory.add("user", query)
        context = self.memory.get_context()

        # --- Retrieve relevant long-term memories ---
        related_memories = self.longterm_memory.search(query, k=3)
        memory_context = "\n".join(related_memories) if related_memories else "None"

        # --- Build the prompt with both contexts ---
        prompt = f"""
        You are NEXCAI, a helpful, polite, and context-aware personal assistant.

        User's relevant long-term memories:
        {memory_context}

        Recent conversation:
        {context}

        Now respond naturally in English to the user's message:
        "{query}"

        Assistant:
        """

        # --- Generate response ---
        response = self.llm.chat(prompt)

        # --- Store new memory (if valuable) ---
        self.longterm_memory.add(query)

        # --- Add assistant reply to short-term memory ---
        self.memory.add("assistant", response)

        return response