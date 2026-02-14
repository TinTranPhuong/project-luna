from typing import List, Dict, Any
from .llama_cpp_adapter import LlamaCppAdapter
from server.src.core.prompts.manager import PromptManager
from server.src.config.settings import get_model_path
from datetime import datetime

class LLMManager:
    def __init__(self):
        # Initialize with the default model defined in settings
        self.current_model_key = "default"
        self.model_path = get_model_path(self.current_model_key)
        
        # Initialize the adapter
        self.provider = LlamaCppAdapter(model_path=self.model_path, n_ctx=25000)
        self.prompt_manager = PromptManager()

    async def initialize(self):
        print(f"Initializing LLM with model: {self.current_model_key}")
        await self.provider.initialize()

    async def generate_response(self, messages: List[Dict[str, Any]], settings: Dict[str, Any] = None) -> str:
        if settings is None: settings = {}
        if "max_tokens" not in settings: settings["max_tokens"] = 8192
        if "temperature" not in settings: settings["temperature"] = 0.5

        # If yes, skip PromptManager and pass raw messages.
        last_msg = messages[-1]["content"] if messages else ""
        if isinstance(last_msg, list):
             return await self.provider.generate(messages, settings)

        formatted_messages = self.prompt_manager.build_messages(messages)
        return await self.provider.generate(formatted_messages, settings)
    
    async def stream_chat(self, messages: List[Dict[str, Any]], settings: Dict[str, Any] = None):
        if settings is None: settings = {}
        if "max_tokens" not in settings: settings["max_tokens"] = 8192
        if "temperature" not in settings: settings["temperature"] = 0.5

        # Vision models need the raw list of dicts, not a formatted string.
        last_msg = messages[-1]["content"] if messages else ""
        
        if isinstance(last_msg, list):
            # Pass RAW messages to the adapter
            print("Vision Request detected: Bypassing Prompt Manager")
            async for chunk in self.provider.stream(messages, settings):
                yield chunk
        else:
            # Normal Text Request
            formatted_messages = self.prompt_manager.build_messages(messages)
            async for chunk in self.provider.stream(formatted_messages, settings):
                yield chunk