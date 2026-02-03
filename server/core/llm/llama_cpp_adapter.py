import os
import logging
from typing import List, Dict, Any, AsyncGenerator
try:
    from llama_cpp import Llama
except ImportError:
    raise ImportError("❌ llama-cpp-python not installed. Run the CUDA install steps!")

from .base import BaseLLMAdapter

logger = logging.getLogger("luna.core.llm.llama")

class LlamaCppAdapter(BaseLLMAdapter):
    def __init__(self, model_filename: str):
        # Resolve path relative to this file
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.model_path = os.path.join(base_path, "models", model_filename)
        self.llm = None
        
    async def initialize(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"❌ Model file not found at: {self.model_path}")
            
        logger.info(f"🚀 Loading GPU Model: {self.model_path}...")
        
        try:
            # RTX 5060Ti Configuration
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=4096,          # Context window (Adjust based on VRAM)
                n_gpu_layers=-1,     # -1 = Offload ALL layers to GPU
                verbose=True,        # Set True to see CUDA logs in terminal
                n_threads=6          # CPU threads for preprocessing
            )
            logger.info("✅ Model loaded successfully on GPU!")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Llama: {e}")
            raise e

    async def generate(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> str:
        # Llama.cpp handles the chat formatting automatically
        output = self.llm.create_chat_completion(
            messages=messages,
            temperature=settings.get("temperature", 0.7),
            max_tokens=settings.get("max_tokens", 1024),
            stream=False
        )
        return output["choices"][0]["message"]["content"]

    async def stream(self, messages: List[Dict[str, str]], settings: Dict[str, Any]) -> AsyncGenerator[str, None]:
        stream = self.llm.create_chat_completion(
            messages=messages,
            temperature=settings.get("temperature", 0.7),
            max_tokens=settings.get("max_tokens", 1024),
            stream=True
        )
        for chunk in stream:
            delta = chunk["choices"][0]["delta"]
            if "content" in delta:
                yield delta["content"]