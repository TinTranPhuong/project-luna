import os
from pathlib import Path

# 1. Dynamic Path Resolution
# This ensures it works on any computer (Windows/Linux/Mac)
# Structure: server/src/config/settings.py -> server/src
SRC_ROOT = Path(__file__).resolve().parent.parent
MODEL_DIR = SRC_ROOT / "models"

# 2. Model Registry
# This is the "Switchboard" for your agents.
# You can map different "Intents" to specific GGUF files here.
MODEL_REGISTRY = {
    # The default general-purpose brain
    "default": "Qwen2.5-VL-7B-Instruct-Q4_K_M.gguf",
    
    # Future: A smaller, faster model for simple tasks
    "fast": "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf",
    
    # Future: A specialized coding model
    "coding": "DeepSeek-R1-Distill-Qwen-14B-Q4_K_M.gguf",
    
    # Future: A vision-specific model
    "vision": "mmproj-Qwen2.5-VL-7B-Instruct-bf16.gguf" 
}

def get_model_path(model_key: str = "default") -> str:
    """
    Returns the absolute path to the requested model.
    Falls back to 'default' if the key is missing.
    """
    filename = MODEL_REGISTRY.get(model_key, MODEL_REGISTRY["default"])
    model_path = MODEL_DIR / filename
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
        
    return str(model_path)

# --- CONTEXT MANAGEMENT ---
# The maximum number of past messages to send to the AI
# 10 is a safe number for a 7B model (keeps context focused)
MAX_HISTORY_MESSAGES = 10 

# (Optional) Maximum tokens if we want to be precise later
MAX_CONTEXT_TOKENS = 4096