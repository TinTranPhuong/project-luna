from llama_cpp import Llama
from typing import List, Dict, Any
import os

class LlamaCppAdapter:
    # We change 'model_filename' to 'model_path' to match the Manager
    def __init__(self, model_path: str, n_ctx: int = 8192):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.llm = None

    async def initialize(self):
        print(f"Adapter loading model from: {self.model_path}")
        
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file missing at: {self.model_path}")

        # RTX 5060 Ti Configuration
        self.llm = Llama(
            model_path=self.model_path,
            n_ctx=self.n_ctx,    # Context Window
            n_gpu_layers=-1,     # -1 = All layers to GPU
            verbose=False,       # Clean logs
        )
        print("✅ GPU Model Loaded Successfully.")

    async def generate(self, messages: List[Dict[str, Any]], settings: Dict[str, Any]) -> str:
        if not self.llm:
            await self.initialize()

        # Simple conversion of chat format to prompt
        # (Llama.cpp handles the specific model templates like <|im_start|> internally now)
        response = self.llm.create_chat_completion(
            messages=messages,
            max_tokens=settings.get("max_tokens", 8192),
            temperature=settings.get("temperature", 0.5),
            stream=False
        )
        
        return response["choices"][0]["message"]["content"]