from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator

class BaseLLMAdapter(ABC):
    """
    Abstract Base Class for all LLM providers.
    Enforces a consistent interface for Ollama, llama.cpp, etc.
    """
    
    @abstractmethod
    async def initialize(self) -> None:
        """Startup logic (loading models, warming up VRAM)."""
        pass

    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
        """
        Generate a complete response string.
        """
        pass

    @abstractmethod
    async def stream(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Stream the response token by token.
        """
        pass