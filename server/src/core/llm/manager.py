import gc
from typing import List, Dict, Any, Optional
from .llama_cpp_adapter import LlamaCppAdapter
from server.src.core.prompts.manager import PromptManager
from server.src.config.settings import get_model_path, MAX_CONTEXT_TOKENS, MAX_NEW_TOKENS
from server.src.agents.types import AgentConfig
import asyncio

# ==============================================================================
# LLM ORCHESTRATION MANAGER
# ==============================================================================

class LLMManager:
    """
    Central controller for the active Large Language Model.
    Manages VRAM allocation, model hot-swapping, and generation pipelines 
    while preserving the global CUDA thread context.
    """
    
    def __init__(self):
        self.current_model_key = "default"
        self.model_path = get_model_path(self.current_model_key)
        self.provider = LlamaCppAdapter(model_path=self.model_path, n_ctx=MAX_CONTEXT_TOKENS)
        self.prompt_manager = PromptManager()

    # --- LIFECYCLE & VRAM MANAGEMENT ---

    async def initialize(self):
        """
        Allocates the model into VRAM. Safe to call concurrently; the adapter 
        will bypass loading if the model is already active.
        """
        if self.provider is None:
            print(f"Manager: Recreating adapter for '{self.current_model_key}'...")
            new_path = get_model_path(self.current_model_key or "default")
            self.provider = LlamaCppAdapter(model_path=new_path, n_ctx=MAX_CONTEXT_TOKENS)

        print(f"Manager: Initializing model '{self.current_model_key}'...")
        await self.provider.initialize()

    def unload_model(self):
        """
        Frees the LLM object from VRAM while intentionally preserving the adapter 
        shell and the global CUDA thread. Ensures clean context reuse on the next initialization.
        """
        if self.provider:
            print("Manager: Unloading LLM from VRAM (Preserving CUDA thread)...")
            self.provider.close()
            gc.collect()
            print("Manager: LLM unloaded. CUDA thread is preserved for reload.")

    async def _switch_model_if_needed(self, model_key: str):
        """
        Executes a model hot-swap. Unloads the current architecture and loads 
        the requested weights into the existing CUDA thread.
        """
        if self.provider is None:
            print(f"Manager: Provider missing, recreating for '{model_key}'...")
            self.current_model_key = model_key
            new_path = get_model_path(model_key)
            self.provider = LlamaCppAdapter(model_path=new_path, n_ctx=MAX_CONTEXT_TOKENS)
            await self.provider.initialize()
            return

        if model_key == self.current_model_key and self.provider.llm is not None:
            return

        if model_key != self.current_model_key:
            print(f"Manager: Switching model {self.current_model_key} -> {model_key}")
            new_path = get_model_path(model_key)
            if not new_path:
                print(f"Manager: No path for '{model_key}', keeping current.")
                return

            self.provider.close()
            self.provider.model_path = new_path
            self.current_model_key = model_key

        await self.provider.initialize()

    # --- INFERENCE PIPELINES ---

    # STRICT TYPING 
    async def generate_response(self, messages: List[Dict[str, Any]], settings: Optional[Dict[str, Any]] = None) -> str:
        """Executes a standard, blocking chat generation request."""
        if settings is None:
            settings = {}
            
        if self.provider is None:
            await self.initialize()
            
        if self.current_model_key == "gpt-oss":
            return await self.provider.generate(messages, settings)    
             
        formatted_messages = self.prompt_manager.build_messages(messages)
        return await self.provider.generate(formatted_messages, settings)

    # STRICT TYPING
    async def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        agent_config: Optional[AgentConfig] = None,
        settings: Optional[Dict[str, Any]] = None,
    ):
        """
        Orchestrates the full streaming pipeline: hot-swaps models if required, 
        injects agent configurations, applies dynamic context, and yields generation chunks.
        """
        if settings is None:
            settings = {}
            
        # CENTRALIZED VARIABLE 
        if "max_tokens" not in settings:
            settings["max_tokens"] = MAX_NEW_TOKENS

        # --- 1. MODEL RESOLUTION ---
        target_model = agent_config.model if agent_config else "default"
        await self._switch_model_if_needed(target_model)

        # --- 2. CONFIGURATION INJECTION ---
        if agent_config:
            settings["temperature"] = agent_config.temperature
            if hasattr(agent_config, "top_k"): settings["top_k"] = agent_config.top_k
            if hasattr(agent_config, "top_p"): settings["top_p"] = agent_config.top_p
            if hasattr(agent_config, "min_p"): settings["min_p"] = agent_config.min_p
            if hasattr(agent_config, "repeat_penalty"): settings["repeat_penalty"] = agent_config.repeat_penalty

        # --- 3. SYSTEM PROMPT INJECTION ---
        if agent_config and agent_config.system_prompt:
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {"role": "system", "content": agent_config.system_prompt})
            else:
                messages[0]["content"] = agent_config.system_prompt

        # --- 4. GENERATION STREAM ---
        last_msg = messages[-1]["content"] if messages else ""

        if isinstance(last_msg, list) or target_model == "gpt-oss":
            print(f"Bypassing Prompt Formatter for {target_model}")
            async for chunk in self.provider.stream(messages, settings):
                yield chunk
        else:
            formatted_messages = self.prompt_manager.build_messages(messages)
            async for chunk in self.provider.stream(formatted_messages, settings):
                yield chunk