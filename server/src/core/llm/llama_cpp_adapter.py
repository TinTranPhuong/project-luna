from llama_cpp import Llama
from llama_cpp.llama_chat_format import Qwen3VLChatHandler
from typing import List, Dict, Any, AsyncGenerator
import os
import json
import asyncio
from concurrent.futures import ThreadPoolExecutor
from server.src.config.settings import MMPROJ_PATH

class LlamaCppAdapter:
    def __init__(self, model_path: str, n_ctx: int = 25000):
        self.model_path = model_path
        # Qwen 3 VL supports large context, 20k is a good safe default
        self.n_ctx = n_ctx 
        self.llm = None
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def initialize(self):
        """Initialize the model in a thread to avoid blocking the event loop"""
        print(f"Adapter loading Qwen 3 VL from: {self.model_path}")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file missing at: {self.model_path}")

        # Run the blocking initialization in a thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._load_model_sync)
        
        print("Qwen 3 VL Model Loaded Successfully.")

    def _load_model_sync(self):
        """Synchronous model loading - runs in thread pool"""
        chat_handler = None
        
        if os.path.exists(MMPROJ_PATH):
            print(f"Vision Adapter found: {MMPROJ_PATH}")
            try:
                chat_handler = Qwen3VLChatHandler(clip_model_path=MMPROJ_PATH)
                print("Qwen 3 Vision Handler Initialized")
            except Exception as e:
                print(f"Failed to load Qwen 3 Vision Handler: {e}")
                # Don't raise - allow text-only mode if vision fails
                chat_handler = None
        else:
            print("No Vision Adapter (mmproj) found. Running in Text-Only mode.")

        # Load the model
        try:
            self.llm = Llama(
                model_path=self.model_path,
                chat_handler=chat_handler,
                n_ctx=self.n_ctx,    
                n_gpu_layers=-1, # Offload all layers to GPU    
                verbose=False,

                type_k=8,             # 8 = GGML_TYPE_Q8_0
                type_v=8,             # 8 = GGML_TYPE_Q8_0
                flash_attn=True
            )
        except Exception as e:
            print(f"CRITICAL: Failed to load model: {e}")
            raise

    async def generate(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
        if not self.llm: 
            await self.initialize()

        # Qwen 3 uses ChatML standard stop tokens
        stop_tokens = ["<|im_end|>", "<|endoftext|>"]

        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            self._executor,
            lambda: self.llm.create_chat_completion(
                messages=messages,
                max_tokens=settings.get("max_tokens", 8192),
                temperature=settings.get("temperature", 0.5),
                stop=stop_tokens,
                repeat_penalty=1.1,
                stream=False
            )
        )
        return response["choices"][0]["message"]["content"]
    
    async def stream(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> AsyncGenerator[str, None]:
        if not self.llm: 
            await self.initialize()
        
        # Qwen 3 Stop Tokens
        stop_tokens = ["<|im_end|>", "<|endoftext|>"]

        print(f"Qwen 3 Streaming started... (Stop tokens: {stop_tokens})")

        stream = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=settings.get("max_tokens", 8192),
            temperature=settings.get("temperature", 0.5),
            stop=stop_tokens, 
            repeat_penalty=1.1,
            stream=True 
        )
        
        chunk_count = 0
        for chunk in stream:
            # Crucial: Yield control to event loop to prevent freezing
            await asyncio.sleep(0) 

            # Handle standard OpenAI-format chunks
            if isinstance(chunk, dict):
                choices = chunk.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        chunk_count += 1
                        yield content
        
        print(f"Stream finished. Chunks sent: {chunk_count}")

    def __del__(self):
        """Cleanup executor on deletion"""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)