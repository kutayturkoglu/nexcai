from pathlib import Path
import os
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from core.utils.llm_interface import LLMInterface


class LongTermMemory:
    """
    FAISS-based vector database for persistent user-specific memory.
    Uses an LLM to decide which pieces of information are worth storing.
    """

    def __init__(self, base_dir=None):
        # --- dynamic base directory ---
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent  # => core/memory/
        os.makedirs(base_dir, exist_ok=True)

        self.index_path = base_dir / "faiss_index.bin"
        self.meta_path  = base_dir / "memories.json"

        # --- embeddings + LLM ---
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.llm = LLMInterface(model="llama3:8b")

        # --- load FAISS index ---
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        else:
            self.index = faiss.IndexFlatL2(self.dimension)

        # --- load stored text metadata ---
        if self.meta_path.exists():
            with open(self.meta_path, "r") as f:
                self.memories = json.load(f)
        else:
            self.memories = []

    # ---------------------------------------------------------------
    # LLM check — is this fact worth remembering?
    # ---------------------------------------------------------------
    def _is_memorable(self, text: str) -> bool:
        prompt = f"""
        You are NEXCAI, a highly selective assistant memory filter.

        Decide if this statement contains meaningful, personal, or factual information 
        about the user that should be stored in long-term memory.

        Examples of "YES":
        - "I live in Munich."
        - "I'm studying Data Science at LMU."
        - "My favorite weather is rainy."
        - "Tomorrow I will have an interview at Sony."

        Examples of "NO":
        - "Hi"
        - "Okay"
        - "Thank you"
        - "What time is it?"

        Respond ONLY with 'YES' or 'NO'.

        Text: "{text}"
        """

        result = self.llm.chat(prompt).strip().lower()
        return result.startswith("yes")

    # ---------------------------------------------------------------
    # Add new memory entry (LLM-filtered)
    # ---------------------------------------------------------------
    def add(self, text: str):
        if not self._is_memorable(text):
            return  # skip if LLM says not important

        # check duplicates
        if self.memories:
            matches = self.search(text, k=1)
            if matches:
                from difflib import SequenceMatcher
                ratio = SequenceMatcher(None, text.lower(), matches[0].lower()).ratio()
                if ratio > 0.8:
                    return  # skip duplicate-like

        # encode + store
        vector = self.model.encode([text])
        self.index.add(np.array(vector, dtype=np.float32))
        self.memories.append(text)
        self._save()

    # ---------------------------------------------------------------
    # Search by similarity
    # ---------------------------------------------------------------
    def search(self, query: str, k: int = 3):
        if len(self.memories) == 0:
            return []
        q_vec = self.model.encode([query])
        D, I = self.index.search(np.array(q_vec, dtype=np.float32), k)
        results = [self.memories[i] for i in I[0] if i < len(self.memories)]
        return results

    # ---------------------------------------------------------------
    # Save FAISS index + metadata
    # ---------------------------------------------------------------
    def _save(self):
        faiss.write_index(self.index, str(self.index_path))
        with open(self.meta_path, "w") as f:
            json.dump(self.memories, f, indent=2)
