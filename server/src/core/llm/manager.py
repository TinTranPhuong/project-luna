from typing import List, Dict, Any
from .llama_cpp_adapter import LlamaCppAdapter
from server.src.core.prompts.manager import PromptManager
from server.src.config.settings import get_model_path
from server.src.agents.types import AgentConfig 
import asyncio

class LLMManager:
    def __init__(self):
        # Initialize with a default, but we will swap it dynamically
        self.current_model_key = "default" 
        self.model_path = get_model_path(self.current_model_key)
        
        # Initialize the adapter
        self.provider = LlamaCppAdapter(model_path=self.model_path, n_ctx=8192) # Increased ctx
        self.prompt_manager = PromptManager()

    async def initialize(self):
        print(f"Initializing LLM with model: {self.current_model_key}")
        await self.provider.initialize()

    async def _switch_model_if_needed(self, model_key: str):
        """
        Checks if the requested model is loaded. If not, unloads current and loads new.
        """
        if model_key != self.current_model_key:
            print(f"Switching Model: {self.current_model_key} -> {model_key}")
            
            # 1. Update paths
            self.current_model_key = model_key
            new_path = get_model_path(model_key)
            
            if not new_path:
                print(f"Warning: No path found for {model_key}, falling back to default.")
                return

            # 2. Re-initialize Provider (Hot Swap)
            # This releases the old RAM/VRAM and loads the new GGUF
            self.provider = LlamaCppAdapter(model_path=new_path, n_ctx=8192)
            await self.provider.initialize()
            print(f"Model Swapped Successfully.")
        else:
            print(f"Model '{model_key}' is already loaded.")

    async def generate_response(self, messages: List[Dict[str, Any]], settings: Dict[str, Any] = None) -> str:
        # Legacy method (kept for compatibility)
        if settings is None: settings = {}
        formatted_messages = self.prompt_manager.build_messages(messages)
        return await self.provider.generate(formatted_messages, settings)
    
    async def stream_chat(self, messages: List[Dict[str, Any]], agent_config: AgentConfig = None, settings: Dict[str, Any] = None):
        if settings is None: settings = {}
        if "max_tokens" not in settings: settings["max_tokens"] = 4096

        # 1. Handle Model Switching
        if agent_config:
            # Inject Agent Temperature
            settings["temperature"] = agent_config.temperature
            # Switch the physical model (GGUF)
            await self._switch_model_if_needed(agent_config.model)
        
        # 2. Handle System Prompt
        # If the agent has a specific brain (system prompt), ensure it's used.
        # Note: We usually prepend this to messages if not present.
        if agent_config and agent_config.system_prompt:
            # Check if system prompt is already at the start
            if not messages or messages[0].get('role') != 'system':
                messages.insert(0, {"role": "system", "content": agent_config.system_prompt})
            elif messages[0].get('role') == 'system':
                # Override existing system prompt
                messages[0]['content'] = agent_config.system_prompt

        # 3. Generate
        last_msg = messages[-1]["content"] if messages else ""
        
        if isinstance(last_msg, list):
            # Pass RAW messages (Vision)
            print("Vision Request: Bypassing Prompt Formatter")
            async for chunk in self.provider.stream(messages, settings):
                yield chunk
        else:
            # Normal Text Request
            formatted_messages = self.prompt_manager.build_messages(messages)
            async for chunk in self.provider.stream(formatted_messages, settings):
                yield chunk