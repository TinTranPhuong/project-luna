from typing import List, Dict, Any
from .llm.llama_cpp_adapter import LlamaCppAdapter

class LLMManager:
    def __init__(self):
        # Ensure this filename MATCHES exactly what is in your server/models folder
        # I recommend downloading a standard text model if the VL one crashes
        self.model_file = "Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf"
        self.provider = LlamaCppAdapter(model_filename=self.model_file)

    async def initialize(self):
        await self.provider.initialize()

    async def generate_response(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
        return await self.provider.generate(messages, settings)