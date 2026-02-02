from functools import lru_cache
from fastapi import Depends
from server.core.llm_manager import LLMManager

# Use lru_cache to ensure we create only one instance of the LLM Manager (Singleton pattern)
@lru_cache()
def get_llm_manager() -> LLMManager:
    return LLMManager()