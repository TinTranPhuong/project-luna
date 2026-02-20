import gc
from typing import List, Dict, Any, Optional
from .llama_cpp_adapter import LlamaCppAdapter
from server.src.core.prompts.manager import PromptManager
from server.src.config.settings import get_model_path
from server.src.agents.types import AgentConfig
import asyncio


class LLMManager:
    def __init__(self):
        self.current_model_key = "default"
        self.model_path = get_model_path(self.current_model_key)
        # Create the adapter once — it holds a reference to the global CUDA thread
        self.provider = LlamaCppAdapter(model_path=self.model_path, n_ctx=8192)
        self.prompt_manager = PromptManager()

    async def initialize(self):
        """
        Load the model into VRAM. Safe to call multiple times — adapter
        skips if already loaded. Also used for handoff recovery.
        """
        if self.provider is None:
            # This should rarely happen now, but keep as a safety net
            print(f"Manager: Recreating adapter for '{self.current_model_key}'...")
            new_path = get_model_path(self.current_model_key or "default")
            self.provider = LlamaCppAdapter(model_path=new_path, n_ctx=8192)

        print(f"Manager: Initializing model '{self.current_model_key}'...")
        await self.provider.initialize()

    def unload_model(self):
        """
        Unload the Llama model from VRAM WITHOUT destroying the adapter or the
        global CUDA thread. This is the fix: the thread stays alive so its
        CUDA context is reused cleanly on the next initialize() call.
        """
        if self.provider:
            print("Manager: Unloading LLM from VRAM (thread stays alive)...")
            # close() frees the Llama object on the CUDA thread but does NOT
            # kill the thread or create a new one on next load.
            self.provider.close()
            # DO NOT set self.provider = None — keep the adapter shell alive
            # DO NOT set self.current_model_key = None
            gc.collect()
            print("Manager: LLM unloaded. CUDA thread is still warm for reload.")

    async def _switch_model_if_needed(self, model_key: str):
        """
        Load a different model if needed. Unloads current first, then loads new,
        both on the same global CUDA thread.
        """
        if self.provider is None:
            print(f"Manager: Provider missing, recreating for '{model_key}'...")
            self.current_model_key = model_key
            new_path = get_model_path(model_key)
            self.provider = LlamaCppAdapter(model_path=new_path, n_ctx=8192)
            await self.provider.initialize()
            return

        # Model already loaded and it's the right one
        if model_key == self.current_model_key and self.provider.llm is not None:
            return

        # Need to switch models
        if model_key != self.current_model_key:
            print(f"Manager: Switching model {self.current_model_key} -> {model_key}")
            new_path = get_model_path(model_key)
            if not new_path:
                print(f"Manager: No path for '{model_key}', keeping current.")
                return

            # Unload current on the CUDA thread
            self.provider.close()

            # Update path and reload on the SAME adapter (same CUDA thread)
            self.provider.model_path = new_path
            self.current_model_key = model_key

        # Load (or reload after unload_model was called)
        await self.provider.initialize()

    async def generate_response(self, messages: List[Dict[str, Any]], settings: Dict[str, Any] = None) -> str:
        if settings is None:
            settings = {}
        if self.provider is None:
            await self.initialize()
        formatted_messages = self.prompt_manager.build_messages(messages)
        return await self.provider.generate(formatted_messages, settings)

    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        agent_config: AgentConfig = None,
        settings: Dict[str, Any] = None,
    ):
        if settings is None:
            settings = {}
        if "max_tokens" not in settings:
            settings["max_tokens"] = 4096

        # 1. Ensure correct model is loaded
        target_model = agent_config.model if agent_config else "default"
        await self._switch_model_if_needed(target_model)

        # 2. Apply agent settings
        if agent_config:
            settings["temperature"] = agent_config.temperature

        # 3. Inject system prompt
        if agent_config and agent_config.system_prompt:
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": agent_config.system_prompt})
            else:
                messages[0]["content"] = agent_config.system_prompt

        # 4. Stream
        last_msg = messages[-1]["content"] if messages else ""

        if isinstance(last_msg, list):
            print("Vision Request: Bypassing Prompt Formatter")
            async for chunk in self.provider.stream(messages, settings):
                yield chunk
        else:
            formatted_messages = self.prompt_manager.build_messages(messages)
            async for chunk in self.provider.stream(formatted_messages, settings):
                yield chunk