from typing import List, Dict, Any
from .llama_cpp_adapter import LlamaCppAdapter
from server.src.core.prompts.manager import PromptManager
from server.src.config.settings import get_model_path

class LLMManager:
    def __init__(self):
        # We initialize with the default model defined in settings
        # In the future, we can add logic here to load multiple adapters 
        # if you want to keep a 'coding' model and a 'chat' model in memory simultaneously
        self.current_model_key = "default"
        self.model_path = get_model_path(self.current_model_key)
        
        # Initialize the adapter with the config-derived path
        self.provider = LlamaCppAdapter(model_path=self.model_path)
        self.prompt_manager = PromptManager()

    async def initialize(self):
        print(f"Initializing LLM with model: {self.current_model_key}")
        await self.provider.initialize()

    async def generate_response(self, messages: List[Dict[str, Any]], settings: Dict[str, Any] = None) -> str:
        if settings is None:
            settings = {}

        # formatting messages with system prompts
        formatted_messages = self.prompt_manager.build_messages(messages)
        
        # In the future, if settings contains 'model': 'coding', 
        # we could switch self.provider here (Hot-Swapping)
        
        return await self.provider.generate(formatted_messages, settings)