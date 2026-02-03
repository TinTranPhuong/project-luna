import aiohttp
import json
import logging
from typing import List, Dict, Any, AsyncGenerator
from .base import BaseLLMAdapter

logger = logging.getLogger("luna.core.llm.ollama")

class OllamaAdapter(BaseLLMAdapter):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        # Default model if none specified. Make sure you have this pulled!
        self.default_model = "luna-qwen" 

    async def initialize(self):
        """Check if Ollama is running and accessible."""
        async with aiohttp.ClientSession() as session:
            try:
                # 'tags' endpoint lists available models
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        logger.info(f"Connected to Ollama at {self.base_url}")
                    else:
                        logger.warning(f"Ollama reachable but returned status {resp.status}")
            except Exception as e:
                logger.error(f"Could not connect to Ollama: {e}")
                logger.error("Make sure Ollama is running! (Run 'ollama serve')")

    async def generate(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
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
        # We will implement streaming in the next step
        yield "Streaming not yet implemented"