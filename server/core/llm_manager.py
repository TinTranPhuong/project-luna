from typing import List, Dict, Any
from .llm.ollama_adapter import OllamaAdapter

class LLMManager:
    """
    Central Manager that handles LLM switching and configuration.
    Currently hardcoded to OllamaAdapter for Phase 1.
    """
    def __init__(self):
        self.provider = OllamaAdapter()

    async def initialize(self):
        """Called on app startup to verify connection"""
        await self.provider.initialize()

    async def generate_response(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
        # Pass request down to the active provider
        return await self.provider.generate(messages, settings)