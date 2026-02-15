from llama_cpp import Llama
from llama_cpp.llama_chat_format import Qwen3VLChatHandler
from typing import List, Dict, Any, AsyncGenerator
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from server.src.config.settings import MMPROJ_PATH

class LlamaCppAdapter:
    def __init__(self, model_path: str, n_ctx: int = 50000):
        self.model_path = model_path
        self.n_ctx = n_ctx 
        self.llm = None
        self._executor = ThreadPoolExecutor(max_workers=1)

    async def initialize(self):
        print(f"Adapter loading model from: {self.model_path}")
        print(f"Context Window: {self.n_ctx} tokens (KV Cache: Q4_0)")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file missing at: {self.model_path}")

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(self._executor, self._load_model_sync)
        print("Model Loaded Successfully.")

    def _load_model_sync(self):
        chat_handler = None
        
        # Always check for Qwen Projector
        is_qwen = "Qwen" in os.path.basename(self.model_path)
        
        if is_qwen and os.path.exists(MMPROJ_PATH):
            print(f"Qwen Model Detected: Loading Vision Adapter...")
            try:
                chat_handler = Qwen3VLChatHandler(clip_model_path=MMPROJ_PATH)
                print("Qwen 3 Vision Handler Attached")
            except Exception as e:
                print(f"Failed to load Vision Handler: {e}")
                chat_handler = None
        else:
            print("Standard Text Model Detected")

        try:
            self.llm = Llama(
                model_path=self.model_path,
                chat_handler=chat_handler,
                n_ctx=self.n_ctx,    
                n_gpu_layers=-1, 
                verbose=False,      
                type_k=2, 
                type_v=2,            
                flash_attn=True
            )
        except Exception as e:
            print(f"CRITICAL: Failed to load model: {e}")
            raise

    async def generate(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
        if not self.llm: await self.initialize()
        stop_tokens = ["<|im_end|>", "<|endoftext|>", "<|end|>"]
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            self._executor,
            lambda: self.llm.create_chat_completion(
                messages=messages,
                max_tokens=settings.get("max_tokens", 8192),
                temperature=settings.get("temperature", 0.6),
                stop=stop_tokens,
                stream=False
            )
        )
        return response["choices"][0]["message"]["content"]
    
    async def stream(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> AsyncGenerator[str, None]:
        if not self.llm: await self.initialize()
        
        stop_tokens = ["<|im_end|>", "<|endoftext|>", "<|end|>"]
        print(f"Streaming started... Model: {os.path.basename(self.model_path)}")

        stream = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=settings.get("max_tokens", 8192),
            temperature=settings.get("temperature", 0.6),
            stop=stop_tokens, 
            stream=True 
        )
        
        # RAW PASS-THROUGH
        for chunk in stream:
            await asyncio.sleep(0) 
            if isinstance(chunk, dict):
                choices = chunk.get("choices", [])
                if choices:
                    delta = choices[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        yield content

    def __del__(self):
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)