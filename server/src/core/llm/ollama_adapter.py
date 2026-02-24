import aiohttp
import json
import logging
from typing import List, Dict, Any, AsyncGenerator
from .base import BaseLLMAdapter

# ==============================================================================
# LOGGER CONFIGURATION
# ==============================================================================
logger = logging.getLogger("luna.core.llm.ollama")

# ==============================================================================
# OLLAMA ADAPTER IMPLEMENTATION
# ==============================================================================

class OllamaAdapter(BaseLLMAdapter):
    """
    Adapter for integrating with a local or remote Ollama instance.
    Handles HTTP session management and payload formatting for the Ollama API.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.default_model = "default" 

    async def initialize(self) -> None:
        """
        Performs a health check against the Ollama server to ensure 
        it is reachable and ready to accept inference requests.
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        logger.info(f"Connected to Ollama at {self.base_url}")
                    else:
                        logger.warning(f"Ollama reachable but returned status {resp.status}")
            except Exception as e:
                logger.error(f"Could not connect to Ollama: {e}")
                logger.error("Make sure Ollama is running! (Run 'ollama server')")

    async def generate(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
        """Sends a synchronous chat request to the Ollama API."""
        url = f"{self.base_url}/api/chat"
        model = settings.get("model") or self.default_model
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": settings.get("temperature", 0.7)
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        raise Exception(f"Ollama Error {resp.status}: {text}")
                    
                    data = await resp.json()
                    return data.get("message", {}).get("content", "")
        except Exception as e:
            logger.error(f"Generate failed: {e}")
            raise e

    async def stream(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> AsyncGenerator[str, None]:
        """
        Placeholder for asynchronous Ollama streaming implementation.
        Currently yields a static fallback string.
        """
        yield "Streaming not yet implemented"