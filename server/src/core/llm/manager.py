from typing import List, Dict, Any
from .llama_cpp_adapter import LlamaCppAdapter
from server.src.core.prompts.manager import PromptManager
from server.src.config.settings import get_model_path

class LLMManager:
    def __init__(self):
        # Initialize with the default model defined in settings
        self.current_model_key = "default"
        self.model_path = get_model_path(self.current_model_key)
        
        # Initialize the adapter with the config-derived path
        self.provider = LlamaCppAdapter(model_path=self.model_path, n_ctx=20000)
        self.prompt_manager = PromptManager()

    async def initialize(self):
        print(f"Initializing LLM with model: {self.current_model_key}")
        await self.provider.initialize()

    async def generate_response(self, messages: List[Dict[str, Any]], settings: Dict[str, Any] = None) -> str:
        """
        Generate a response using the configured LLM.
        """
        if settings is None:
            settings = {}

        # --- FIX: Increase Token Limit ---
        # The default limit is usually too short for summaries. 
        # We force it to 2048 (or higher) to allow full essays.
        if "max_tokens" not in settings:
            settings["max_tokens"] = 8192  # Plenty of space for long summaries
        
        # Optional: Set temperature if missing (0.7 is a good balance)
        if "temperature" not in settings:
            settings["temperature"] = 0.5

        # formatting messages with system prompts
        formatted_messages = self.prompt_manager.build_messages(messages)
        
        # Call the provider with the updated settings
        return await self.provider.generate(formatted_messages, settings)
    
    # ... inside class LLMManager ...

    async def stream_chat(self, messages: List[Dict[str, Any]], settings: Dict[str, Any] = None):
        """
        Stream the response token by token using the adapter.
        """
        if settings is None:
            settings = {}
            
        # Ensure we have limits set
        if "max_tokens" not in settings:
            settings["max_tokens"] = 8192
        if "temperature" not in settings:
            settings["temperature"] = 0.5

        # Format messages using your prompt manager
        formatted_messages = self.prompt_manager.build_messages(messages)
        
        # Use the PROVIDER (Adapter), not 'self.llm'
        async for chunk in self.provider.stream(formatted_messages, settings):
            yield chunk