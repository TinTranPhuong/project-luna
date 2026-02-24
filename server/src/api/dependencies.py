from functools import lru_cache
from fastapi import Depends
from server.src.core.llm.manager import LLMManager

# ==============================================================================
# DEPENDENCY INJECTION
# ==============================================================================

@lru_cache()
def get_llm_manager() -> LLMManager:
    """
    Provides a singleton instance of the LLM Manager.
    Ensures the model is loaded only once and shared across all active requests.
    """
    return LLMManager()